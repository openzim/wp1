import unittest
import unittest.mock

import pymysql.err

from wp1.base_db_test import get_test_connect_creds
from wp1.environment import Environment


class DbTest(unittest.TestCase):

  @unittest.mock.patch('wp1.db.ENV', Environment.DEVELOPMENT)
  @unittest.mock.patch('wp1.db.CREDENTIALS', get_test_connect_creds())
  def test_connect_works_with_creds(self):
    from wp1.db import connect
    self.assertIsNotNone(connect('WP10DB'))
    self.assertIsNotNone(connect('WIKIDB'))

  @unittest.mock.patch('wp1.db.ENV', Environment.DEVELOPMENT)
  @unittest.mock.patch('wp1.db.CREDENTIALS', get_test_connect_creds())
  @unittest.mock.patch('wp1.db.pymysql.connect')
  @unittest.mock.patch('wp1.db.time.sleep')
  def test_retries_four_times_failure(self, patched_sleep, patched_pymysql):
    from wp1.db import connect
    patched_pymysql.side_effect = pymysql.err.InternalError()
    with self.assertRaises(pymysql.err.InternalError):
      connect('WP10DB')
    self.assertEqual(5, patched_pymysql.call_count)
