#!/usr/bin/env python3
"""Seed the WP1 database with schema, global rankings, and namespace data.

This script performs three seeding steps (each can be skipped individually):

  1. Apply setup/schema.sql to create the required database tables.
  2. Seed ``global_rankings`` from the QUALITY/IMPORTANCE maps in
     ``conf/<lang>/conf.json``.
  3. Fetch namespace mappings for the configured wiki from the Wikimedia API
     and seed the ``namespacename`` table.

Usage
-----
  pipenv run python setup/seed.py --db <database> [options]

Examples
--------
  # Seed an Arabic WP1 database running locally:
  pipenv run python setup/seed.py --lang ar --db arwp10 --password secret

  # Seed only rankings (skip schema creation and namespace fetch):
  pipenv run python setup/seed.py --lang ar --db arwp10 --skip-schema --skip-namespaces
"""

import argparse
import json
import logging
import os
import re
import sys

import pymysql
import pymysql.cursors
import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

_HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(_HERE, "schema.sql")
CONF_BASE_PATH = os.path.join(os.path.dirname(_HERE), "conf")

WIKIMEDIA_API_URL = "https://{domain}/w/api.php"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def dbname_to_domain(dbname):
    """Derive a wiki domain from a database name.

    Examples::

      'arwiki_p' -> 'ar.wikipedia.org'
      'enwiki_p' -> 'en.wikipedia.org'
      'frwiki_p' -> 'fr.wikipedia.org'
    """
    name = dbname[:-2] if dbname.endswith("_p") else dbname
    if name.endswith("wiki"):
        lang = name[:-4]
        return f"{lang}.wikipedia.org"
    return name


def strip_sql_comments(sql):
    """Remove SQL line comments and block comments, return executable statements."""
    # Remove block comments (/* ... */ and /** ... **/)
    sql = re.sub(r"/\*[\s\S]*?\*/", "", sql)
    # Remove line comments
    sql = re.sub(r"--[^\n]*", "", sql)
    return sql


# ---------------------------------------------------------------------------
# Seeding steps
# ---------------------------------------------------------------------------


def apply_schema(cursor, schema_path):
    """Execute every CREATE TABLE statement from schema.sql.

    Uses ``CREATE TABLE IF NOT EXISTS`` so the script is safe to run against a
    database that already has some or all tables.
    """
    logger.info("Applying schema from %s", schema_path)
    with open(schema_path, encoding="utf-8") as fh:
        raw_sql = fh.read()

    sql = strip_sql_comments(raw_sql)

    for stmt in sql.split(";"):
        stmt = stmt.strip()
        if not stmt:
            continue
        # Make CREATE TABLE idempotent
        stmt = re.sub(
            r"\bCREATE TABLE\b",
            "CREATE TABLE IF NOT EXISTS",
            stmt,
            flags=re.IGNORECASE,
        )
        try:
            cursor.execute(stmt)
            logger.debug("OK: %.60s…", stmt.replace("\n", " "))
        except pymysql.err.ProgrammingError as exc:
            logger.warning(
                "Skipped statement (%s): %.80s…", exc, stmt.replace("\n", " ")
            )


def seed_global_rankings(cursor, conf):
    """Insert QUALITY and IMPORTANCE rankings from conf.json into global_rankings."""
    logger.info("Seeding global_rankings…")

    rows = []
    for rating, ranking in conf.get("QUALITY", {}).items():
        rows.append(("quality", rating.encode("utf-8"), int(ranking)))
    for rating, ranking in conf.get("IMPORTANCE", {}).items():
        rows.append(("importance", rating.encode("utf-8"), int(ranking)))

    if not rows:
        logger.warning(
            "No QUALITY or IMPORTANCE entries found in conf.json – skipping."
        )
        return

    cursor.executemany(
        """
      INSERT INTO global_rankings (gr_type, gr_rating, gr_ranking)
      VALUES (%s, %s, %s)
      ON DUPLICATE KEY UPDATE gr_ranking = VALUES(gr_ranking)
      """,
        rows,
    )
    logger.info("Upserted %d row(s) into global_rankings.", len(rows))


def fetch_wiki_namespaces(domain):
    """Return (namespaces_dict, aliases_list) from the Wikimedia siteinfo API."""
    url = WIKIMEDIA_API_URL.format(domain=domain)
    params = {
        "action": "query",
        "meta": "siteinfo",
        "siprop": "namespaces|namespacealiases",
        "format": "json",
    }
    headers = {"User-Agent": "wp1bot-seed/1.0 (https://github.com/openzim/wp1)"}
    logger.info("Fetching namespace data from %s", url)
    resp = requests.get(url, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    query = data.get("query", {})
    return query.get("namespaces", {}), query.get("namespacealiases", [])


def seed_namespaces(cursor, dbname, domain, namespaces, aliases):
    """Populate the namespacename table for the given wiki."""
    logger.info("Seeding namespacename for %s (%s)…", dbname, domain)

    dbname_b = dbname.encode("utf-8")
    domain_b = domain.encode("utf-8")
    rows = []

    for ns_id_str, ns_info in namespaces.items():
        ns_id = int(ns_id_str)
        primary_name = ns_info.get("*", "")
        canonical_name = ns_info.get("canonical", "")

        # Primary (localised) name – always present (may be empty string for NS 0)
        rows.append(
            (dbname_b, domain_b, ns_id, primary_name.encode("utf-8"), "primary", 1)
        )

        # Canonical (English) name when it differs from the primary name
        if canonical_name and canonical_name != primary_name:
            rows.append(
                (
                    dbname_b,
                    domain_b,
                    ns_id,
                    canonical_name.encode("utf-8"),
                    "canonical",
                    1,
                )
            )

    for alias_info in aliases:
        alias_name = alias_info.get("*", "")
        ns_id = int(alias_info["id"])
        if alias_name:
            rows.append(
                (dbname_b, domain_b, ns_id, alias_name.encode("utf-8"), "alias", 0)
            )

    if not rows:
        logger.warning("No namespace rows to insert – skipping.")
        return

    cursor.executemany(
        """
      INSERT INTO namespacename (dbname, domain, ns_id, ns_name, ns_type, ns_is_favorite)
      VALUES (%s, %s, %s, %s, %s, %s)
      ON DUPLICATE KEY UPDATE
        ns_id = VALUES(ns_id),
        ns_is_favorite = VALUES(ns_is_favorite)
      """,
        rows,
    )
    logger.info("Upserted %d row(s) into namespacename.", len(rows))


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--lang",
        default="en",
        metavar="LANG",
        help="Language code matching a conf/<lang>/conf.json file (default: en).",
    )
    parser.add_argument(
        "--host", default="localhost", help="MySQL host (default: localhost)."
    )
    parser.add_argument(
        "--port", type=int, default=3306, help="MySQL port (default: 3306)."
    )
    parser.add_argument("--user", default="root", help="MySQL user (default: root).")
    parser.add_argument("--password", default="", help="MySQL password.")
    parser.add_argument("--db", required=True, help="MySQL database name to seed.")
    parser.add_argument(
        "--skip-schema",
        action="store_true",
        help="Skip applying schema.sql (tables must already exist).",
    )
    parser.add_argument(
        "--skip-rankings",
        action="store_true",
        help="Skip seeding global_rankings from conf.json.",
    )
    parser.add_argument(
        "--skip-namespaces",
        action="store_true",
        help="Skip fetching and seeding namespace data from the Wikimedia API.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    conf_path = os.path.join(CONF_BASE_PATH, args.lang, "conf.json")
    if not os.path.isfile(conf_path):
        logger.error(
            "conf.json not found at '%s'. "
            "Pass --lang with a code that matches a directory under conf/.",
            conf_path,
        )
        sys.exit(1)

    with open(conf_path, encoding="utf-8") as fh:
        conf = json.load(fh)

    dbname = conf.get("DATABASE_WIKI_TS", f"{args.lang}wiki_p")
    domain = dbname_to_domain(dbname)

    logger.info(
        "Seeding database=%s  lang=%s  wiki=%s (%s)",
        args.db,
        args.lang,
        dbname,
        domain,
    )

    # Connect without specifying a database first so we can create it if needed.
    conn = pymysql.connect(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{args.db}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            cursor.execute(f"USE `{args.db}`")
            logger.info("Using database %r.", args.db)
            if not args.skip_schema:
                apply_schema(cursor, SCHEMA_PATH)
                conn.commit()

            if not args.skip_rankings:
                seed_global_rankings(cursor, conf)
                conn.commit()

            if not args.skip_namespaces:
                namespaces, aliases = fetch_wiki_namespaces(domain)
                seed_namespaces(cursor, dbname, domain, namespaces, aliases)
                conn.commit()

        logger.info("Done – database %r seeded successfully.", args.db)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
