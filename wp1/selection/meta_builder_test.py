from unittest import TestCase
from unittest.mock import MagicMock, patch

from wp1.exceptions import Wp1FatalSelectionError, Wp1RetryableSelectionError
from wp1.models.wp10.selection import Selection
from wp1.selection.meta_builder import MetaBuilder


def _selection(status: bytes = b"OK", object_key: bytes | None = b"object-key"):
    return Selection(
        s_builder_id=b"builder-a",
        s_content_type=b"text/tab-separated-values",
        s_version=1,
        s_status=status,
        s_object_key=object_key,
    )


class MetaBuilderTest(TestCase):

    def setUp(self):
        self.builder = MetaBuilder()

    @patch("wp1.selection.meta_builder.logic_builder.latest_selection_for")
    def test_fetch_selection_data(self, mock_latest_selection):
        mock_latest_selection.return_value = _selection()
        s3 = MagicMock()
        s3.download_fileobj.side_effect = lambda _key, buf: buf.write(b"first\n")

        actual = self.builder._fetch_selection_data(MagicMock(), s3, "builder-a")

        self.assertEqual(b"first\n", actual)
        s3.download_fileobj.assert_called_once()

    @patch("wp1.selection.meta_builder.logic_builder.latest_selection_for")
    def test_fetch_selection_data_failed_selection(self, mock_latest_selection):
        mock_latest_selection.return_value = _selection(status=b"FAILED")

        with self.assertRaises(Wp1FatalSelectionError):
            self.builder._fetch_selection_data(MagicMock(), MagicMock(), "builder-a")

    @patch("wp1.selection.meta_builder.logic_builder.latest_selection_for")
    def test_fetch_selection_data_retryable_selection(self, mock_latest_selection):
        mock_latest_selection.return_value = _selection(status=b"CAN_RETRY")

        with self.assertRaises(Wp1RetryableSelectionError):
            self.builder._fetch_selection_data(MagicMock(), MagicMock(), "builder-a")

    @patch("wp1.selection.meta_builder.logic_builder.latest_selection_for")
    def test_fetch_selection_data_without_stored_data(self, mock_latest_selection):
        mock_latest_selection.return_value = _selection(object_key=None)

        with self.assertRaisesRegex(Wp1RetryableSelectionError, "no stored data"):
            self.builder._fetch_selection_data(MagicMock(), MagicMock(), "builder-a")

    @patch("wp1.selection.meta_builder.logic_builder.latest_selection_for")
    def test_fetch_selection_data_missing_selection(self, mock_latest_selection):
        mock_latest_selection.return_value = None

        with self.assertRaises(Wp1RetryableSelectionError):
            self.builder._fetch_selection_data(MagicMock(), MagicMock(), "builder-a")
