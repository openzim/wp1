import importlib
import logging
import sys
import unittest

import pymysql

from wp1.credentials import CREDENTIALS, ENV
from wp1.environment import Environment
from wp1.models.wp10.rating import Rating
from wp1.models.wp10.selection import Selection
from wp1.redis_db import connect as redis_connect

logger = logging.getLogger(__name__)


_sql_cache = {}

# Schemas (up.sql filenames) that have already been created in this process.
_schemas_ready = set()

# filename -> {table: AUTO_INCREMENT value expected right after a reset}.
# Used to skip the (slow) ALTER TABLE for tests that never touched the table.
_auto_increment_baselines = {}


def parse_sql(filename):
    if filename in _sql_cache:
        return _sql_cache[filename]

    data = open(filename, "r").readlines()
    stmts = []
    DELIMITER = ";"
    stmt = ""
    for lineno, line in enumerate(data):
        if not line.strip():
            continue

        if line.startswith("--"):
            continue

        if "DELIMITER" in line:
            DELIMITER = line.split()[1]
            continue

        if DELIMITER not in line:
            stmt += line.replace(DELIMITER, ";")
            continue

        if stmt:
            stmt += line
            stmts.append(stmt.strip())
            stmt = ""
        else:
            stmts.append(line.strip())
    _sql_cache[filename] = stmts
    return stmts


def _table_names(down_filename):
    return [stmt.split("`")[1] for stmt in parse_sql(down_filename)]


def _seed_stmts(up_filename):
    return [
        stmt
        for stmt in parse_sql(up_filename)
        if not stmt.upper().startswith("CREATE TABLE")
    ]


def _auto_increment_tables(up_filename):
    tables = []
    for stmt in parse_sql(up_filename):
        if stmt.upper().startswith("CREATE TABLE") and "AUTO_INCREMENT" in stmt.upper():
            tables.append(stmt.split("`")[1] if "`" in stmt else stmt.split()[2])
    return tables


def _read_auto_increments(cursor, tables):
    if not tables:
        return {}
    placeholders = ", ".join(["%s"] * len(tables))
    cursor.execute(
        "SELECT TABLE_NAME, AUTO_INCREMENT FROM information_schema.TABLES "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME IN (%s)" % placeholders,
        tables,
    )
    return {
        row["TABLE_NAME"].decode("utf-8"): row["AUTO_INCREMENT"]
        for row in cursor.fetchall()
    }


def _ensure_schema(conn, up_filename):
    """Creates the test schema, once per process.

    Tables are created only if they don't exist and are never dropped between
    tests; instead each test starts by resetting the table *data* (see
    _reset_tables), which is orders of magnitude faster than DDL.
    """
    if up_filename in _schemas_ready:
        return
    with conn.cursor() as cursor:
        for stmt in parse_sql(up_filename):
            if stmt.upper().startswith("CREATE TABLE"):
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS" + stmt[len("CREATE TABLE") :]
                )
    conn.commit()
    _schemas_ready.add(up_filename)


def _reset_tables(conn, up_filename, down_filename):
    """Restores every table to its pristine post-up.sql state.

    Deletes all rows, resets AUTO_INCREMENT counters that have moved, and
    re-runs the seed INSERTs from the up.sql file.
    """
    auto_inc_tables = _auto_increment_tables(up_filename)
    baseline = _auto_increment_baselines.get(up_filename)
    with conn.cursor() as cursor:
        if auto_inc_tables:
            counters = _read_auto_increments(cursor, auto_inc_tables)

        for table in _table_names(down_filename):
            cursor.execute("DELETE FROM `%s`" % table)

        for table in auto_inc_tables:
            # ALTER is comparatively slow, skip it unless an insert into this
            # table (by a previous test) actually moved the counter.
            if baseline is None or counters[table] != baseline[table]:
                cursor.execute("ALTER TABLE `%s` AUTO_INCREMENT = 1" % table)

        for stmt in _seed_stmts(up_filename):
            cursor.execute(stmt)

        if auto_inc_tables and baseline is None:
            _auto_increment_baselines[up_filename] = _read_auto_increments(
                cursor, auto_inc_tables
            )
    conn.commit()


class WpOneAssertions(unittest.TestCase):

    def assertObjectListsEqual(self, expected, actual):
        self.assertEqual(
            set(
                tuple(sorted((key, value) for key, value in d.items()))
                for d in expected
            ),
            set(
                tuple(sorted((key, value) for key, value in d.items())) for d in actual
            ),
        )


class BaseWpOneDbTest(WpOneAssertions):

    def connect_wp_one_db(self):
        if ENV != Environment.TEST:
            raise ValueError(
                "Database tests destroy data! They should only be run in the TEST env"
            )
        creds = CREDENTIALS.get(Environment.TEST, {}).get("WP10DB")
        if creds is None:
            raise ValueError("No WP10DB creds found")

        return pymysql.connect(
            **creds,
            charset=None,
            use_unicode=False,
            cursorclass=pymysql.cursors.DictCursor
        )

    def _cleanup_wp_one_db(self):
        # Tables are intentionally left in place (with whatever data the test
        # produced); the next test's setup resets them. This avoids paying for
        # DROP/CREATE of the whole schema on every test.
        self.wp10db.close()

    def _setup_wp_one_db(self):
        self.wp10db = self.connect_wp_one_db()
        _ensure_schema(self.wp10db, "wp10_test.up.sql")
        _reset_tables(self.wp10db, "wp10_test.up.sql", "wp10_test.down.sql")

    def connect_redis_db(self):
        if ENV != Environment.TEST:
            raise ValueError(
                "Database tests destroy data! They should only be run in the TEST env"
            )
        return redis_connect()

    def _setup_redis_db(self):
        self.redis = self.connect_redis_db()
        self.redis.ping()
        self.redis.flushdb()

    def _cleanup_redis_db(self):
        self.redis.flushdb()

    def setUp(self):
        self.addCleanup(self._cleanup_wp_one_db)
        self._setup_wp_one_db()

        self.addCleanup(self._cleanup_redis_db)
        self._setup_redis_db()


class BaseWikiDbTest(WpOneAssertions):

    def connect_wiki_db(self):
        if ENV != Environment.TEST:
            raise ValueError(
                "Database tests destroy data! They should only be run in the TEST env"
            )
        creds = CREDENTIALS.get(Environment.TEST, {}).get("WIKIDB")
        if creds is None:
            raise ValueError("No WIKIDB creds found")

        return pymysql.connect(
            **creds,
            charset=None,
            use_unicode=False,
            cursorclass=pymysql.cursors.DictCursor
        )

    def _cleanup_wiki_db(self):
        # See BaseWpOneDbTest._cleanup_wp_one_db: tables persist across tests.
        self.wikidb.close()

    def _setup_wiki_db(self):
        self.wikidb = self.connect_wiki_db()
        _ensure_schema(self.wikidb, "wiki_test.up.sql")
        _reset_tables(self.wikidb, "wiki_test.up.sql", "wiki_test.down.sql")

    def setUp(self):
        self.addCleanup(self._cleanup_wiki_db)
        self._setup_wiki_db()


class BaseCombinedDbTest(BaseWikiDbTest, BaseWpOneDbTest):

    def setUp(self):
        self.addCleanup(self._cleanup_wiki_db)
        self._setup_wiki_db()

        self.addCleanup(self._cleanup_wp_one_db)
        self._setup_wp_one_db()

        self.addCleanup(self._cleanup_redis_db)
        self._setup_redis_db()


def get_first_selection(wp10db):
    with wp10db.cursor() as cursor:
        cursor.execute("SELECT * from selections LIMIT 1")
        db_selection = cursor.fetchone()
        return Selection(**db_selection)


class TestCleanupDb(BaseCombinedDbTest):

    def test_no_op(self):
        # A no-op test to allow for the setup and cleanup to run. Used
        # when a previous test run was interrupted and the test left the
        # databases in a dirty state.
        pass
