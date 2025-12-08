import unittest
from unittest.mock import patch

import wp1.wikilang_db


class WikiLangDbTest(unittest.TestCase):

    @patch("wp1.wikilang_db.db_connect")
    def test_connect(self, mock_connect):
        wp1.wikilang_db.connect("fr")

        mock_connect.assert_called_once_with(
            "WIKIDB", host="frwiki.analytics.db.svc.eqiad.wmflabs", db="frwiki_p"
        )
