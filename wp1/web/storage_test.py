from unittest.mock import patch, MagicMock

import flask

from wp1.environment import Environment
from wp1.web.base_web_testcase import BaseWebTestcase
from wp1.web.storage import has_storage, get_storage


class StorageTest(BaseWebTestcase):

  def test_has_storage_empty(self):
    with self.app.app_context():
      self.assertFalse(has_storage())

  def test_has_storage_exists(self):
    with self.override_db(self.app), self.app.app_context():
      self.assertTrue(has_storage())

  def test_does_not_connect_if_no_creds(self):
    with self.app.app_context():
      with self.assertRaises(ValueError):
        actual = get_storage()

  @patch('wp1.web.storage.KiwixStorage')
  def test_get_storage_does_not_connect_if_existing(self, patched_kiwixstorage):
    with self.override_db(self.app), self.app.app_context():
      actual = get_storage()
      patched_kiwixstorage.assert_not_called()

  @patch(
      'wp1.web.storage.CREDENTIALS', {
          Environment.DEVELOPMENT: {
              'STORAGE': {
                  'key': 'test_key',
                  'secret': 'test_secret',
                  'bucket': 'org-kiwix-dev-wp1',
              }
          }
      })
  def test_get_storage_raises_if_no_env(self):
    with self.app.app_context():
      with self.assertRaises(ValueError):
        actual = get_storage()

  @patch('wp1.web.storage.ENV', Environment.DEVELOPMENT)
  def test_get_storage_raises_if_no_credentials(self):
    with self.app.app_context():
      with self.assertRaises(ValueError):
        actual = get_storage()

  @patch('wp1.web.storage.CREDENTIALS', {Environment.DEVELOPMENT: {}})
  @patch('wp1.web.storage.ENV', Environment.DEVELOPMENT)
  def test_get_storage_raises_if_no_storage_key(self):
    with self.app.app_context():
      with self.assertRaises(ValueError):
        actual = get_storage()

  @patch(
      'wp1.web.storage.CREDENTIALS', {
          Environment.DEVELOPMENT: {
              'STORAGE': {
                  'key': 'test_key',
                  'secret': 'test_secret',
                  'bucket': 'org-kiwix-dev-wp1',
              }
          }
      })
  @patch('wp1.web.storage.ENV', Environment.DEVELOPMENT)
  @patch('wp1.web.storage.KiwixStorage')
  def test_get_storage_connects_to_kiwixstorage(self, patched_kiwixstorage):
    with self.app.app_context():
      actual = get_storage()
      patched_kiwixstorage.assert_called_once_with(
          'https://s3.us-west-1.wasabisys.com/'
          '?keyId=test_key&secretAccessKey=test_secret&bucketName=org-kiwix-dev-wp1'
      )

  @patch(
      'wp1.web.storage.CREDENTIALS', {
          Environment.DEVELOPMENT: {
              'STORAGE': {
                  'key': 'test_key',
                  'secret': 'test_secret',
                  'bucket': 'org-kiwix-dev-wp1',
              }
          }
      })
  @patch('wp1.web.storage.ENV', Environment.DEVELOPMENT)
  @patch('wp1.web.storage.KiwixStorage')
  def test_get_storage_checks_permissions(self, patched_kiwixstorage):
    s3_mock = MagicMock()
    patched_kiwixstorage.return_value = s3_mock
    with self.app.app_context():
      actual = get_storage()
      s3_mock.check_credentials.assert_called_once_with(list_buckets=True,
                                                        bucket=True,
                                                        write=True,
                                                        read=True)

  @patch(
      'wp1.web.storage.CREDENTIALS', {
          Environment.DEVELOPMENT: {
              'STORAGE': {
                  'key': 'test_key',
                  'secret': 'test_secret',
                  'bucket': 'org-kiwix-dev-wp1',
              }
          }
      })
  @patch('wp1.web.storage.ENV', Environment.DEVELOPMENT)
  @patch('wp1.web.storage.KiwixStorage')
  def test_get_storage_sets_storage(self, patched_kiwixstorage):
    with self.app.app_context() as ctx:
      actual = get_storage()
      self.assertTrue(hasattr(flask.g, 'storage'))

  @patch(
      'wp1.web.storage.CREDENTIALS', {
          Environment.DEVELOPMENT: {
              'STORAGE': {
                  'key': 'test_key',
                  'secret': 'test_secret',
                  'bucket': 'org-kiwix-dev-wp1',
              }
          }
      })
  @patch('wp1.web.storage.ENV', Environment.DEVELOPMENT)
  @patch('wp1.web.storage.KiwixStorage')
  def test_get_storage_returns_s3_from_kiwixstorage(self, patched_kiwixstorage):
    s3_mock = MagicMock()
    patched_kiwixstorage.return_value = s3_mock
    with self.app.app_context() as ctx:
      actual = get_storage()
      self.assertEqual(s3_mock, actual)
