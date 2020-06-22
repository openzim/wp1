import importlib
import unittest
from unittest.mock import MagicMock, patch

import mwclient

import wp1.api


class ApiWithCredsTest(unittest.TestCase):

  @patch('wp1.api.get_credentials')
  @patch('wp1.api.mwclient.Site')
  def test_login(self, patched_mwsite, patched_credentials):
    site = patched_mwsite()
    wp1.api.login()
    self.assertEqual(1, site.login.call_count)

  @patch('wp1.api.get_credentials')
  @patch('wp1.api.mwclient.Site')
  @patch('wp1.api.logger')
  def test_login_exception(self, patched_logger, patched_mwsite,
                           patched_credentials):
    site = patched_mwsite()
    site.login.side_effect = mwclient.errors.LoginError()
    wp1.api.login()
    self.assertEqual(1, patched_logger.exception.call_count)


class ApiTest(unittest.TestCase):

  def setUp(self):
    self.page = MagicMock()
    self.original_save_page = wp1.api.save_page

  @patch('wp1.api.site')
  def test_save_page(self, patched_site):
    wp1.api.save_page(self.page, '<code>', 'edit summary')
    self.assertEqual(1, self.page.save.call_count)
    self.assertEqual(('<code>', 'edit summary'), self.page.save.call_args[0])

  @patch('wp1.api.site')
  @patch('wp1.api.login')
  @patch('wp1.api.get_page')
  def test_save_page_retries_on_exception(self, patched_get_page, patched_login,
                                          patched_site):
    self.page.save.side_effect = mwclient.errors.AssertUserFailedError()
    wp1.api.save_page(self.page, '<code>', 'edit summary')
    self.assertEqual(1, patched_login.call_count)
    self.assertEqual(1, patched_get_page.call_count)

  @patch('wp1.api')
  def test_save_page_skips_login_on_none_site(self, patched_api):
    patched_api.site = None
    actual = self.original_save_page(self.page, '<code>', 'edit summary')
    self.assertFalse(actual)

  def test_get_revision_id_present(self):
    self.page.revisions.return_value = iter(({'revid': 10},))
    actual = wp1.api.get_revision_id_by_timestamp(self.page,
                                                  '2015-05-05T15:55:55Z')
    self.assertEquals(10, actual)

  def test_get_revision_id_absent(self):
    self.page.revisions.return_value = iter(())
    actual = wp1.api.get_revision_id_by_timestamp(self.page,
                                                  '2015-05-05T15:55:55Z')
    self.assertIsNone(actual)
