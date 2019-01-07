import unittest
import pymysql


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
  def _setup_wp_one_db(self):
    self.wp10db = pymysql.connect(
      host='localhost',
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

  def _teardown_wp_one_db(self):
    stmts = parse_sql('wp10_test.down.sql')
    with self.wp10db.cursor() as cursor:
      for stmt in stmts:
        cursor.execute(stmt)
    self.wp10db.commit()
    self.wp10db.close()

  def setUp(self):
    self._setup_wp_one_db()

  def tearDown(self):
    self._teardown_wp_one_db()


class BaseWikiDbTest(unittest.TestCase):
  def _setup_wiki_db(self):
    self.wikidb = pymysql.connect(
      host='localhost',
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

  def _teardown_wiki_db(self):
    stmts = parse_sql('wiki_test.down.sql')
    with self.wikidb.cursor() as cursor:
      for stmt in stmts:
        cursor.execute(stmt)
    self.wikidb.commit()
    self.wikidb.close()

  def setUp(self):
    self._setup_wiki_db()

  def tearDown(self):
    self._teardown_wiki_db()


class BaseCombinedDbTest(BaseWikiDbTest, BaseWpOneDbTest):
  def setUp(self):
    self._setup_wiki_db()
    self._setup_wp_one_db()

  def tearDown(self):
    self._teardown_wiki_db()
    self._teardown_wp_one_db()
