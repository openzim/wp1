import unittest
from unittest.mock import MagicMock, patch

from wp1.config import override_settings
from wp1.storage import connect_storage


class StorageTest(unittest.TestCase):

    @override_settings(STORAGE_KEY="", STORAGE_SECRET="")
    def test_connect_storage_raises_if_no_credentials(self):
        with self.assertRaises(ValueError):
            connect_storage()

    @override_settings(STORAGE_KEY="")
    def test_connect_storage_raises_if_no_storage_key(self):
        with self.assertRaises(ValueError):
            connect_storage()

    @override_settings(
        STORAGE_URL="https://test.wasabisys.fake",
        STORAGE_KEY="test_key",
        STORAGE_SECRET="test_secret",
        STORAGE_BUCKET="org-kiwix-dev-wp1",
    )
    @patch("wp1.storage.KiwixStorage")
    def test_connect_storage_connects_to_kiwixstorage(self, patched_kiwixstorage):
        connect_storage()
        patched_kiwixstorage.assert_called_once_with(
            "https://test.wasabisys.fake/"
            "?keyId=test_key&secretAccessKey=test_secret&bucketName=org-kiwix-dev-wp1"
        )

    @override_settings(
        STORAGE_URL="https://test.wasabisys.fake",
        STORAGE_KEY="test_key",
        STORAGE_SECRET="test_secret",
        STORAGE_BUCKET="org-kiwix-dev-wp1",
    )
    @patch("wp1.storage.KiwixStorage")
    def test_connect_storage_checks_permissions(self, patched_kiwixstorage):
        s3_mock = MagicMock()
        patched_kiwixstorage.return_value = s3_mock
        connect_storage()
        s3_mock.check_credentials.assert_called_once_with(
            list_buckets=True, bucket=True, write=True, read=True
        )
