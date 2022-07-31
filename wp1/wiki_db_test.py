import unittest
import unittest.mock

from wp1.environment import Environment
from wp1 import wiki_db


class WikiDbTest(unittest.TestCase):

  def test_connect_works(self):
    self.assertIsNotNone(wiki_db.connect())
