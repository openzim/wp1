import importlib
import logging
import unittest
import sys

import pymysql

from wp1.environment import Environment
from wp1.models.wp10.selection import Selection

logger = logging.getLogger(__name__)

try:
  from wp1.credentials import CREDENTIALS, ENV
except ImportError:
  logger.exception('The credentials.py file must be populated to run tests.')
  CREDENTIALS = None
  ENV = None


def parse_sql(filename):
  data = open(filename, 'r').readlines()
  stmts = []
  DELIMITER = ';'
  stmt = ''
  for lineno, line in enumerate(data):
    if not line.strip():
      continue

    if line.startswith('--'):
      continue

    if 'DELIMITER' in line:
      DELIMITER = line.split()[1]
      continue

    if (DELIMITER not in line):
      stmt += line.replace(DELIMITER, ';')
      continue

    if stmt:
      stmt += line
      stmts.append(stmt.strip())
      stmt = ''
    else:
      stmts.append(line.strip())
  return stmts


class WpOneAssertions(unittest.TestCase):

  def assertObjectListsEqual(self, expected, actual):
    self.assertEqual(
        set(
            tuple(sorted((key, value)
                         for key, value in d.items()))
            for d in expected),
        set(
            tuple(sorted((key, value)
                         for key, value in d.items()))
            for d in actual))


class BaseWpOneDbTest(WpOneAssertions):

  def connect_wp_one_db(self):
    if ENV != Environment.TEST:
      raise ValueError(
          'Database tests destroy data! They should only be run in the TEST env'
      )
    creds = CREDENTIALS.get(Environment.TEST, {}).get('WP10DB')
    if creds is None:
      raise ValueError('No WP10DB creds found')

    return pymysql.connect(**creds,
                           charset=None,
                           use_unicode=False,
                           cursorclass=pymysql.cursors.DictCursor)

  def _cleanup_wp_one_db(self):
    stmts = parse_sql('wp10_test.down.sql')
    with self.wp10db.cursor() as cursor:
      for stmt in stmts:
        cursor.execute(stmt)
    self.wp10db.commit()
    self.wp10db.close()

  def _setup_wp_one_db(self):
    self.wp10db = self.connect_wp_one_db()
    stmts = parse_sql('wp10_test.up.sql')
    with self.wp10db.cursor() as cursor:
      for stmt in stmts:
        cursor.execute(stmt)
    self.wp10db.commit()

  def setUp(self):
    self.addCleanup(self._cleanup_wp_one_db)
    self._setup_wp_one_db()


class BaseWikiDbTest(WpOneAssertions):

  def connect_wiki_db(self):
    if ENV != Environment.TEST:
      raise ValueError(
          'Database tests destroy data! They should only be run in the TEST env'
      )
    creds = CREDENTIALS.get(Environment.TEST, {}).get('WIKIDB')
    if creds is None:
      raise ValueError('No WIKIDB creds found')

    return pymysql.connect(**creds,
                           charset=None,
                           use_unicode=False,
                           cursorclass=pymysql.cursors.DictCursor)

  def _cleanup_wiki_db(self):
    stmts = parse_sql('wiki_test.down.sql')
    with self.wikidb.cursor() as cursor:
      for stmt in stmts:
        cursor.execute(stmt)
    self.wikidb.commit()
    self.wikidb.close()

  def _setup_wiki_db(self):
    self.wikidb = self.connect_wiki_db()
    stmts = parse_sql('wiki_test.up.sql')
    with self.wikidb.cursor() as cursor:
      for stmt in stmts:
        cursor.execute(stmt)
    self.wikidb.commit()

  def setUp(self):
    self.addCleanup(self._cleanup_wiki_db)
    self._setup_wiki_db()


class BaseCombinedDbTest(BaseWikiDbTest, BaseWpOneDbTest):

  def setUp(self):
    self.addCleanup(self._cleanup_wiki_db)
    self._setup_wiki_db()

    self.addCleanup(self._cleanup_wp_one_db)
    self._setup_wp_one_db()


def get_first_selection(wp10db):
  with wp10db.cursor() as cursor:
    cursor.execute('SELECT * from selections LIMIT 1')
    db_selection = cursor.fetchone()
    return Selection(**db_selection)
