import importlib
import unittest
import unittest
import unittest.mock
import sys

import pymysql

from wp1.environment import Environment


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


class BaseWpOneDbTest(unittest.TestCase):

  def _cleanup_wp_one_db(self):
    stmts = parse_sql('wp10_test.down.sql')
    with self.wp10db.cursor() as cursor:
      for stmt in stmts:
        cursor.execute(stmt)
    self.wp10db.commit()
    self.wp10db.close()

  def _setup_wp_one_db(self):
    self.wp10db = pymysql.connect(host='localhost',
                                  db='enwp10_test',
                                  user='root',
                                  charset=None,
                                  use_unicode=False,
                                  cursorclass=pymysql.cursors.DictCursor)
    stmts = parse_sql('wp10_test.up.sql')
    with self.wp10db.cursor() as cursor:
      for stmt in stmts:
        cursor.execute(stmt)
    self.wp10db.commit()

  def setUp(self):
    self.addCleanup(self._cleanup_wp_one_db)
    self._setup_wp_one_db()


class BaseWikiDbTest(unittest.TestCase):

  def _cleanup_wiki_db(self):
    stmts = parse_sql('wiki_test.down.sql')
    with self.wikidb.cursor() as cursor:
      for stmt in stmts:
        cursor.execute(stmt)
    self.wikidb.commit()
    self.wikidb.close()

  def _setup_wiki_db(self):
    self.wikidb = pymysql.connect(host='localhost',
                                  db='enwikip_test',
                                  user='root',
                                  charset=None,
                                  use_unicode=False,
                                  cursorclass=pymysql.cursors.DictCursor)
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


def get_test_connect_creds():
  return {
      Environment.DEVELOPMENT: {
          'WP10DB': {
              'user': 'root',
              'host': 'localhost',
              'db': 'enwp10_test',
          },
          'WIKIDB': {
              'user': 'root',
              'host': 'localhost',
              'db': 'enwikip_test',
          }
      },
      Environment.PRODUCTION: {}
  }
