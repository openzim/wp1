import importlib
import unittest
import unittest.mock
import sys

import pymysql.err

import wp1.wiki_db


class WikiDbImportTest(unittest.TestCase):

  def test_connect_method_returns_none_with_no_creds(self):
    self.assertIsNone(wp1.wiki_db.connect())


class WikiDbTest(unittest.TestCase):
  WIKI_CREDS = {
      'user': 'root',
      'host': 'localhost',
      'db': 'enwikip_test',
  }

  def setUp(self):
    creds = unittest.mock.MagicMock()
    creds.WIKI_CREDS = self.WIKI_CREDS
    sys.modules['wp1.credentials'] = creds
    importlib.reload(wp1.wiki_db)

  def test_connect_works_with_creds(self):
    from wp1.wiki_db import connect
    self.assertIsNotNone(connect())

  @unittest.mock.patch('wp1.wiki_db.pymysql.connect')
  @unittest.mock.patch('wp1.wiki_db.time.sleep')
  def test_retries_four_times_failure(self, patched_sleep, patched_pymysql):
    from wp1.wiki_db import connect
    patched_pymysql.side_effect = pymysql.err.InternalError()
    with self.assertRaises(pymysql.err.InternalError):
      connect()
    self.assertEquals(5, patched_pymysql.call_count)
