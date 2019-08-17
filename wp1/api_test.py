import unittest
from unittest.mock import MagicMock, patch

import mwclient

from wp1 import api

class ApiTest(unittest.TestCase):
  def setUp(self):
    self.page = MagicMock()

  def test_save_page(self):
    api.save_page(self.page, '<code>', 'edit summary')
    self.assertEqual(1, len(self.page.save.call_args_list))
    self.assertEqual(('<code>', 'edit summary'), self.page.save.call_args[0])

  @patch('wp1.api.login')
  def test_save_page_tries_login_on_exception(self, patched_login):
    self.page.save.side_effect = mwclient.errors.AssertUserFailedError()
    with self.assertRaises(mwclient.errors.AssertUserFailedError):
      actual = api.save_page(self.page, '<code>', 'edit summary')
      self.assertTrue(actual)
      self.assertEqual(1, len(patched_login.call_args_listx))

  def test_save_page_skips_login_on_none_site(self):
    api.site = None
    actual = api.save_page(self.page, '<code>', 'edit summary')
    self.assertFalse(actual)
