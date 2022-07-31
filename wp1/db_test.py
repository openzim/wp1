import unittest
from unittest.mock import patch

import pymysql.err

from wp1.environment import Environment


class DbTest(unittest.TestCase):

  def test_connect_works(self):
    from wp1.db import connect
    self.assertIsNotNone(connect('WP10DB'))
    self.assertIsNotNone(connect('WIKIDB'))

  @patch('wp1.db.ENV', Environment.PRODUCTION)
  def test_exception_thrown_with_empty_creds(self):
    from wp1.db import connect
    with self.assertRaises(ValueError):
      connect('WP10DB')

    with self.assertRaises(ValueError):
      self.assertIsNotNone(connect('WIKIDB'))

  @patch('wp1.db.pymysql.connect')
  @patch('wp1.db.time.sleep')
  def test_retries_four_times_failure(self, patched_sleep, patched_pymysql):
    from wp1.db import connect
    patched_pymysql.side_effect = pymysql.err.InternalError()
    with self.assertRaises(pymysql.err.InternalError):
      connect('WP10DB')
    self.assertEqual(5, patched_pymysql.call_count)
