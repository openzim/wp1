import json
from datetime import timedelta
from unittest.mock import patch

from wp1.base_db_test import BaseWpOneDbTest
from wp1.logic import sites as logic_sites

SITEMATRIX_RESULT = {
    "sitematrix": {
        "count": 3,
        "0": {
            "code": "aa",
            "name": "Qaf\u00e1r af",
            "site": [
                {
                    "url": "https://aa.wikipedia.org",
                    "dbname": "aawiki",
                    "code": "wiki",
                    "sitename": "Wikipedia",
                    "closed": "",
                },
                {
                    "url": "https://aa.wiktionary.org",
                    "dbname": "aawiktionary",
                    "code": "wiktionary",
                    "sitename": "Wiktionary",
                    "closed": "",
                },
            ],
            "dir": "ltr",
            "localname": "Afar",
        },
        "1": {
            "code": "ab",
            "name": "\u0410\u04a7\u0441\u0448\u04d9\u0430",
            "site": [
                {
                    "url": "https://ab.wikipedia.org",
                    "dbname": "abwiki",
                    "code": "wiki",
                    "sitename": "\u0410\u0432\u0438\u043a\u0438\u043f\u0435\u0434\u0438\u0430",
                },
            ],
            "dir": "ltr",
            "localname": "Abkhazian",
        },
        "specials": [
            {
                "url": "https://commons.wikimedia.org",
                "dbname": "commonswiki",
                "code": "commons",
                "lang": "commons",
                "sitename": "Wikimedia Commons",
            },
        ],
    },
}

EXPECTED_PROJECTS = ["aa.wikipedia.org", "aa.wiktionary.org", "ab.wikipedia.org"]

EXPECTED_DBNAMES = {
    "aa.wikipedia.org": "aawiki",
    "aa.wiktionary.org": "aawiktionary",
    "ab.wikipedia.org": "abwiki",
    "commons.wikimedia.org": "commonswiki",
}


class SitesTest(BaseWpOneDbTest):

    @patch("wp1.logic.sites.mwclient.Site")
    def test_get_site_data_fetches_and_caches(self, patched_site):
        patched_site.return_value.api.return_value = SITEMATRIX_RESULT

        actual = logic_sites.get_site_data(self.redis)

        self.assertEqual(EXPECTED_PROJECTS, actual["projects"])
        self.assertEqual(EXPECTED_DBNAMES, actual["dbnames"])

        cached = json.loads(self.redis.get(logic_sites.CACHE_KEY))
        self.assertEqual(actual, cached)

        # A second call is served from the cache, without another fetch.
        self.assertEqual(actual, logic_sites.get_site_data(self.redis))
        patched_site.assert_called_once()

    @patch("wp1.logic.sites.mwclient.Site")
    def test_get_site_data_cached(self, patched_site):
        data = {"projects": EXPECTED_PROJECTS, "dbnames": EXPECTED_DBNAMES}
        self.redis.setex(
            logic_sites.CACHE_KEY, timedelta(days=1), value=json.dumps(data)
        )

        actual = logic_sites.get_site_data(self.redis)

        self.assertEqual(data, actual)
        patched_site.assert_not_called()

    @patch("wp1.logic.sites.mwclient.Site")
    def test_get_projects(self, patched_site):
        patched_site.return_value.api.return_value = SITEMATRIX_RESULT
        self.assertEqual(EXPECTED_PROJECTS, logic_sites.get_projects(self.redis))

    @patch("wp1.logic.sites.mwclient.Site")
    def test_dbname_for_project(self, patched_site):
        patched_site.return_value.api.return_value = SITEMATRIX_RESULT
        self.assertEqual(
            "aawiki", logic_sites.dbname_for_project(self.redis, "aa.wikipedia.org")
        )
        self.assertEqual(
            "commonswiki",
            logic_sites.dbname_for_project(self.redis, "commons.wikimedia.org"),
        )

    @patch("wp1.logic.sites.mwclient.Site")
    def test_dbname_for_project_unknown(self, patched_site):
        patched_site.return_value.api.return_value = SITEMATRIX_RESULT
        self.assertIsNone(
            logic_sites.dbname_for_project(self.redis, "not.a.project.fake")
        )

    @patch("wp1.logic.sites.mwclient.Site")
    def test_get_site_data_unparseable_cache(self, patched_site):
        patched_site.return_value.api.return_value = SITEMATRIX_RESULT
        self.redis.setex(logic_sites.CACHE_KEY, timedelta(days=1), value=b"{not json")

        actual = logic_sites.get_site_data(self.redis)

        self.assertEqual(EXPECTED_PROJECTS, actual["projects"])
        patched_site.assert_called_once()
