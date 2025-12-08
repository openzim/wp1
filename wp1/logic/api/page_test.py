from datetime import datetime
import time
import unittest
from unittest.mock import MagicMock, patch

import wp1.logic.api.page as api_page


class TestApiPage(unittest.TestCase):

    @patch("wp1.logic.api.page.site")
    def test_get_redirect(self, patched_site):
        patched_site.api.return_value = {
            "query": {
                "redirects": [
                    {
                        "to": "Foo Bar Baz",
                    }
                ],
                "pages": {
                    "Foo Bar": {
                        "ns": 0,
                        "title": "Foo Bar Baz",
                        "revisions": [
                            {
                                "timestamp": "2018-12-25T01:02:03Z",
                            }
                        ],
                    }
                },
            }
        }

        actual = api_page.get_redirect("0:Foo_Bar")
        self.assertEqual(0, actual["ns"])
        self.assertEqual("Foo_Bar_Baz", actual["title"])
        self.assertEqual(datetime(2018, 12, 25, 1, 2, 3), actual["timestamp_dt"])

    @patch("wp1.logic.api.page.site")
    def test_get_moves(self, patched_site):
        patched_site.logevents.return_value = [
            {
                "params": {
                    "target_ns": 0,
                    "target_title": "Foo Bar Baz",
                },
                "timestamp": time.gmtime(1545699723),
            }
        ]

        actual = api_page.get_moves("0:Foo_Bar")
        self.assertIsNotNone(actual)
        self.assertEqual(1, len(actual))
        self.assertEqual(0, actual[0]["ns"])
        self.assertEqual("Foo_Bar_Baz", actual[0]["title"])
        self.assertEqual(datetime(2018, 12, 25, 1, 2, 3), actual[0]["timestamp_dt"])

    @patch("wp1.logic.api.page.site")
    def test_get_move_replace_namespace(self, patched_site):
        patched_site.logevents.return_value = [
            {
                "params": {
                    "target_ns": 14,
                    "target_title": "Category:Foo Bar Baz",
                },
                "timestamp": time.gmtime(1545699723),
            }
        ]
        actual = api_page.get_moves("14:Foo_Bar")
        self.assertIsNotNone(actual)
        self.assertEqual(1, len(actual))
        self.assertEqual(14, actual[0]["ns"])
        self.assertEqual("Foo_Bar_Baz", actual[0]["title"])
        self.assertEqual(datetime(2018, 12, 25, 1, 2, 3), actual[0]["timestamp_dt"])
