import unittest
import unittest.mock

from wp1.environment import Environment
from wp1 import wp10_db


class Wp10DbTest(unittest.TestCase):

    def test_connect_works(self):
        self.assertIsNotNone(wp10_db.connect())
