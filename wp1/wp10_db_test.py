import unittest
import unittest.mock

from wp1.base_db_test import get_test_connect_creds
from wp1.environment import Environment
from wp1 import wp10_db


class Wp10DbTest(unittest.TestCase):

  @unittest.mock.patch('wp1.db.ENV', Environment.DEVELOPMENT)
  @unittest.mock.patch('wp1.db.CREDENTIALS', get_test_connect_creds())
  def test_connect_works_with_creds(self):
    self.assertIsNotNone(wp10_db.connect())
