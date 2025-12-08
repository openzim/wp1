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

    @patch("wp1.web.storage.connect_storage")
    def test_get_storage_does_not_connect_if_existing(self, patched_connect_storage):
        with self.override_db(self.app), self.app.app_context():
            actual = get_storage()
            patched_connect_storage.assert_not_called()

    @patch("wp1.web.storage.connect_storage")
    def test_get_storage_sets_storage(self, patched_connect_storage):
        with self.app.app_context():
            actual = get_storage()
            self.assertTrue(hasattr(flask.g, "storage"))

    @patch("wp1.web.storage.connect_storage")
    def test_get_storage_returns_s3(self, patched_connect_storage):
        s3_mock = MagicMock()
        patched_connect_storage.return_value = s3_mock
        with self.app.app_context():
            actual = get_storage()
            self.assertEqual(s3_mock, actual)
