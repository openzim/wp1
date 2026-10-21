import pickle
from datetime import datetime
from unittest.mock import MagicMock, patch

from wp1 import npp
from wp1.base_db_test import BaseCombinedDbTest


class NppTest(BaseCombinedDbTest):
    project = b"Catholicism"

    pages = [
        (1, 0, b"Saint_Foo", 0, 0, b"20261001120000"),
        (2, 0, b"Saint_Bar", 0, 0, b"20260915080000"),
        (3, 0, b"Reviewed_Church", 0, 1, b"20261002000000"),
        (4, 0, b"Redirect_Church", 1, 0, b"20261003000000"),
        (5, 2, b"Some_User/Draft", 0, 0, b"20261004000000"),
        (6, 0, b"Other_Project_Article", 0, 0, b"20261005000000"),
    ]

    ratings = [
        (b"Catholicism", b"Saint_Foo", b"Stub-Class", b"Low-Class"),
        (b"Catholicism", b"Saint_Bar", b"Start-Class", None),
        (b"Catholicism", b"Reviewed_Church", b"C-Class", b"Mid-Class"),
        (b"Catholicism", b"Redirect_Church", b"Redirect-Class", None),
        (b"Catholicism", b"Unpatrolled_Elsewhere", b"Stub-Class", None),
        (b"Water", b"Other_Project_Article", b"Stub-Class", b"Low-Class"),
    ]

    def setUp(self):
        super().setUp()
        with self.wikidb.cursor() as cursor:
            for page_id, ns, title, is_redirect, reviewed, created in self.pages:
                cursor.execute(
                    """
                  INSERT INTO page
                    (page_id, page_namespace, page_title, page_is_redirect)
                  VALUES (%s, %s, %s, %s)
                """,
                    (page_id, ns, title, is_redirect),
                )
                cursor.execute(
                    """
                  INSERT INTO pagetriage_page
                    (ptrp_page_id, ptrp_reviewed, ptrp_created)
                  VALUES (%s, %s, %s)
                """,
                    (page_id, reviewed, created),
                )
        self.wikidb.commit()

        with self.wp10db.cursor() as cursor:
            for project, article, quality, importance in self.ratings:
                cursor.execute(
                    """
                  INSERT INTO ratings
                    (r_project, r_namespace, r_article, r_quality, r_importance)
                  VALUES (%s, 0, %s, %s, %s)
                """,
                    (project, article, quality, importance),
                )
        self.wp10db.commit()

    def test_fetch_backlog(self):
        actual = npp.fetch_backlog(self.wikidb)
        self.assertEqual(
            {
                b"Saint_Foo": b"20261001120000",
                b"Saint_Bar": b"20260915080000",
                b"Other_Project_Article": b"20261005000000",
            },
            actual,
        )

    def test_get_backlog_caches(self):
        expected = npp.get_backlog(self.redis, self.wikidb)
        wikidb = MagicMock()

        actual = npp.get_backlog(self.redis, wikidb)

        self.assertEqual(expected, actual)
        self.assertLessEqual(self.redis.ttl(npp.BACKLOG_KEY), 3600)
        wikidb.cursor.assert_not_called()

    def test_get_backlog_uses_cache(self):
        cached = {b"Cached_Article": b"20260101000000"}
        self.redis.set(npp.BACKLOG_KEY, pickle.dumps(cached))
        wikidb = MagicMock()

        actual = npp.get_backlog(self.redis, wikidb)

        self.assertEqual(cached, actual)
        wikidb.cursor.assert_not_called()

    def test_get_project_articles(self):
        backlog = npp.fetch_backlog(self.wikidb)
        actual = npp.get_project_articles(self.wp10db, self.project, backlog)
        self.assertEqual(
            [
                {
                    "title": "Saint Bar",
                    "created": datetime(2026, 9, 15, 8),
                    "quality": b"Start-Class",
                    "importance": None,
                },
                {
                    "title": "Saint Foo",
                    "created": datetime(2026, 10, 1, 12),
                    "quality": b"Stub-Class",
                    "importance": b"Low-Class",
                },
            ],
            actual,
        )

    @patch("wp1.npp.BATCH_SIZE", 1)
    def test_get_project_articles_batches(self):
        backlog = npp.fetch_backlog(self.wikidb)
        actual = npp.get_project_articles(self.wp10db, self.project, backlog)
        self.assertEqual(["Saint Bar", "Saint Foo"], [a["title"] for a in actual])

    def test_get_project_articles_empty_backlog(self):
        actual = npp.get_project_articles(self.wp10db, self.project, {})
        self.assertEqual([], actual)

    def test_create_wikicode(self):
        backlog = npp.fetch_backlog(self.wikidb)
        articles = npp.get_project_articles(self.wp10db, self.project, backlog)

        actual = npp.create_wikicode(self.project, articles)

        self.assertEqual(
            "<noinclude>{{Automatically generated}}</noinclude>\n"
            "2 articles tagged by WikiProject Catholicism are waiting for review by "
            "[[Wikipedia:New pages patrol|New Pages Patrol]], oldest first.\n\n"
            '{| class="wikitable sortable"\n'
            "! Article !! Created !! Quality !! Importance\n"
            "|-\n"
            "| [[Saint Bar]] || 2026-09-15 || Start-Class || \n"
            "|-\n"
            "| [[Saint Foo]] || 2026-10-01 || Stub-Class || Low-Importance\n"
            "|}",
            actual,
        )

    def test_create_wikicode_no_articles(self):
        actual = npp.create_wikicode(b"Water_polo", [])
        self.assertEqual(
            "<noinclude>{{Automatically generated}}</noinclude>\n"
            "No articles tagged by WikiProject Water polo are waiting for review by "
            "[[Wikipedia:New pages patrol|New Pages Patrol]].",
            actual,
        )

    def _upload(self, project_name):
        wikidb = MagicMock(wraps=self.wikidb)
        wp10db = MagicMock(wraps=self.wp10db)
        wikidb.close = MagicMock()
        wp10db.close = MagicMock()
        with (
            patch("wp1.npp.wiki_connect", return_value=wikidb),
            patch("wp1.npp.wp10_connect", return_value=wp10db),
            patch("wp1.npp.redis_connect", return_value=self.redis),
        ):
            npp.upload_project_npp_table(project_name)
        wikidb.close.assert_called_once()
        wp10db.close.assert_called_once()

    @patch("wp1.npp.api")
    def test_upload_project_npp_table(self, patched_api):
        page = patched_api.get_page.return_value

        self._upload(self.project)

        patched_api.get_page.assert_called_once_with(
            "User:WP 1.0 bot/Tables/Project/Catholicism/NPP"
        )
        patched_api.save_page.assert_called_once()
        call = patched_api.save_page.call_args[0]
        self.assertEqual(page, call[0])
        self.assertIn("[[Saint Foo]]", call[1])
        self.assertEqual("Update New Pages Patrol article list.", call[2])

    @patch("wp1.npp.api")
    def test_upload_project_npp_table_no_articles_new_page(self, patched_api):
        patched_api.get_page.return_value.exists = False

        self._upload(b"Physics")

        patched_api.save_page.assert_not_called()

    @patch("wp1.npp.api")
    def test_upload_project_npp_table_no_articles_existing_page(self, patched_api):
        patched_api.get_page.return_value.exists = True

        self._upload(b"Physics")

        call = patched_api.save_page.call_args[0]
        self.assertIn("No articles tagged by WikiProject Physics", call[1])

    @patch("wp1.npp.api")
    def test_upload_project_npp_table_no_site(self, patched_api):
        patched_api.get_page.return_value = None

        self._upload(self.project)

        patched_api.save_page.assert_not_called()
