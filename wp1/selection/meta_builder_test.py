from unittest import TestCase
from unittest.mock import MagicMock, patch

from botocore.exceptions import ClientError

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

        with self.assertRaises(Wp1FatalSelectionError) as context:
            self.builder._fetch_selection_data(MagicMock(), MagicMock(), "builder-a")

        self.assertEqual(
            "REFERENCED_SELECTION_FAILED", context.exception.extra["dependency_code"]
        )
        self.assertEqual(
            "latest selection failed", context.exception.extra["dependency_reason"]
        )

    @patch("wp1.selection.meta_builder.logic_builder.latest_selection_for")
    def test_fetch_selection_data_retryable_selection(self, mock_latest_selection):
        mock_latest_selection.return_value = _selection(status=b"CAN_RETRY")

        with self.assertRaises(Wp1RetryableSelectionError) as context:
            self.builder._fetch_selection_data(MagicMock(), MagicMock(), "builder-a")

        self.assertEqual(
            "REFERENCED_SELECTION_RETRYABLE_FAILURE",
            context.exception.extra["dependency_code"],
        )
        self.assertEqual(
            "latest selection failed but can be retried",
            context.exception.extra["dependency_reason"],
        )
        self.assertEqual(
            "Open this list and retry it, then retry this Combinator.",
            context.exception.extra["dependency_action"],
        )

    @patch("wp1.selection.meta_builder.logic_builder.latest_selection_for")
    def test_fetch_selection_data_without_stored_data(self, mock_latest_selection):
        mock_latest_selection.return_value = _selection(object_key=None)

        with self.assertRaisesRegex(Wp1RetryableSelectionError, "no stored data"):
            self.builder._fetch_selection_data(MagicMock(), MagicMock(), "builder-a")

    @patch("wp1.selection.meta_builder.logic_builder.latest_selection_for")
    def test_fetch_selection_data_missing_selection(self, mock_latest_selection):
        mock_latest_selection.return_value = None

        with self.assertRaises(Wp1RetryableSelectionError) as context:
            self.builder._fetch_selection_data(MagicMock(), MagicMock(), "builder-a")

        self.assertEqual(
            "REFERENCED_SELECTION_MISSING", context.exception.extra["dependency_code"]
        )

    @patch("wp1.selection.meta_builder.logic_builder.latest_selection_for")
    def test_fetch_selection_data_download_error(self, mock_latest_selection):
        mock_latest_selection.return_value = _selection(object_key=b"object-key")
        s3 = MagicMock()
        s3.download_fileobj.side_effect = ClientError(
            {"Error": {"Code": "NoSuchKey"}}, "GetObject"
        )

        with self.assertRaises(Wp1RetryableSelectionError) as context:
            self.builder._fetch_selection_data(MagicMock(), s3, "builder-a")

        self.assertEqual(
            "REFERENCED_SELECTION_DOWNLOAD_FAILED",
            context.exception.extra["dependency_code"],
        )
        self.assertEqual(
            "could not download the latest selection",
            context.exception.extra["dependency_reason"],
        )
        self.assertEqual("object-key", context.exception.extra["object_key"])
        self.assertEqual("NoSuchKey", context.exception.extra["storage_error_code"])
