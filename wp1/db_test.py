import unittest
from unittest.mock import MagicMock, patch

import pymysql.err
import socks

from wp1.environment import Environment


class DbTest(unittest.TestCase):

    def test_connect_works(self):
        from wp1.db import connect

        self.assertIsNotNone(connect("WP10DB"))
        self.assertIsNotNone(connect("WIKIDB"))

    @patch("wp1.db.ENV", Environment.PRODUCTION)
    def test_exception_thrown_with_empty_creds(self):
        from wp1.db import connect

        with self.assertRaises(ValueError):
            connect("WP10DB")

        with self.assertRaises(ValueError):
            self.assertIsNotNone(connect("WIKIDB"))

    @patch("wp1.db.pymysql.connect")
    @patch("wp1.db.time.sleep")
    def test_retries_four_times_failure(self, patched_sleep, patched_pymysql):
        from wp1.db import connect

        patched_pymysql.side_effect = pymysql.err.InternalError()
        with self.assertRaises(pymysql.err.InternalError):
            connect("WP10DB")
        self.assertEqual(5, patched_pymysql.call_count)

    @patch("wp1.db.pymysql.connect")
    @patch("wp1.db.socks.socksocket")
    @patch("wp1.db.ENV", Environment.DEVELOPMENT)
    def test_socks_proxy(self, mock_socket, mock_connect):
        from wp1.db import connect

        socket = MagicMock()
        mock_socket.return_value = socket
        conn = MagicMock()
        mock_connect.return_value = conn

        connect("WIKIDB", host="foo.wikimedia.cloud", port=6000)

        socket.set_proxy.assert_called_once_with(socks.SOCKS5, "localhost")
        socket.connect.assert_called_once_with(("foo.wikimedia.cloud", 6000))
        defer = mock_connect.call_args.kwargs.get("defer_connect")
        self.assertTrue(defer)
        conn.connect.assert_called_once_with(sock=socket)

    @patch("wp1.db.pymysql.connect")
    @patch("wp1.db.socks.socksocket")
    @patch("wp1.db.ENV", Environment.DEVELOPMENT)
    def test_socks_proxy_not_used(self, mock_socket, mock_connect):
        from wp1.db import connect

        connect("WP10DB")
        mock_socket.assert_not_called()
        mock_connect.assert_called_once()
