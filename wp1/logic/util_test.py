import unittest

from wp1.logic import util


class TestUtil(unittest.TestCase):
  safe_name_tests = [
      ('Foo Bar', 'FooBar'),
      ('Français', 'Français'),
      ('âme île & **hôtel-sûr_être', 'âmeîlehôtel-sûr_être'),
      ('爱', '爱'),
  ]

  def test_safe_name(self):
    for test, expected in self.safe_name_tests:
      actual = util.safe_name(test)
      self.assertEqual(expected, actual)
