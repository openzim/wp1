import unittest

import fakeredis


class BaseRedisTest(unittest.TestCase):

  def setUp(self):
    self.redis = fakeredis.FakeStrictRedis()

  def tearDown(self):
    self.redis = None
