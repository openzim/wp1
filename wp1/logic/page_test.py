from datetime import datetime
from unittest.mock import patch
import time

import attr

from wp1.base_db_test import BaseWikiDbTest, BaseWpOneDbTest, BaseCombinedDbTest
from wp1.constants import TS_FORMAT
from wp1.logic import page as logic_page
from wp1.logic import project as logic_project
from wp1.logic import log as logic_log
from wp1.models.wp10.log import Log
from wp1.models.wp10.move import Move
from wp1.models.wp10.namespace import Namespace, NsType
from wp1.models.wp10.project import Project
from wp1.models.wiki.page import Page


def get_all_moves(wp10db):
    with wp10db.cursor() as cursor:
        cursor.execute("SELECT * FROM " + Move.table_name)
        return [Move(**db_move) for db_move in cursor.fetchall()]


def get_all_logs(redis):
    return logic_log.get_logs(redis)


class LogicPageCategoryTest(BaseWikiDbTest):

    def setUp(self):
        super().setUp()
        ts = datetime(2018, 9, 30, 12, 30, 0)
        with self.wikidb.cursor() as cursor:
            pages = [
                {"id": 100, "ns": 0, "title": b"The cape of Superman"},
                {"id": 101, "ns": 0, "title": b"Powers of Superman"},
                {"id": 102, "ns": 14, "title": b"Places Superman vacations"},
                {"id": 103, "ns": 14, "title": b"Superman Facts"},
            ]
            for page in pages:
                cursor.execute(
                    """
            INSERT INTO page
              (page_id, page_namespace, page_title)
            VALUES
              (%(id)s, %(ns)s, %(title)s)
        """,
                    page,
                )
            cls = [
                {"from": 100, "to": b"Articles about Superman", "timestamp": ts},
                {"from": 101, "to": b"Articles about Superman", "timestamp": ts},
                {"from": 102, "to": b"Articles about Superman", "timestamp": ts},
                {"from": 103, "to": b"Articles about Superman", "timestamp": ts},
            ]
            for cl in cls:
                cursor.execute(
                    """
            INSERT INTO categorylinks
              (cl_from, cl_to, cl_timestamp)
            VALUES
              (%(from)s, %(to)s, %(timestamp)s)
        """,
                    cl,
                )
        self.wikidb.commit()

    def test_get_category_pages(self):
        titles = set()
        for page in logic_page.get_pages_by_category(
            self.wikidb, b"Articles about Superman"
        ):
            titles.add(page.page_title)

        self.assertEqual(4, len(titles))
        self.assertTrue(b"The cape of Superman" in titles)
        self.assertTrue(b"Powers of Superman" in titles)
        self.assertTrue(b"Places Superman vacations" in titles)
        self.assertTrue(b"Superman Facts" in titles)

    def test_get_category_pages_ns_filter(self):
        titles = set()
        for page in logic_page.get_pages_by_category(
            self.wikidb, b"Articles about Superman", ns=14
        ):
            titles.add(page.page_title)

        self.assertEqual(2, len(titles))
        self.assertTrue(b"Superman Facts" in titles)
        self.assertTrue(b"Places Superman vacations" in titles)


class LogicPageMovesTest(BaseCombinedDbTest):

    def setUp(self):
        super().setUp()
        self.timestamp_str = "2011-04-28T12:30:00Z"
        self.expected_ns = 0
        self.expected_title = "Article_moved_to"
        self.expected_dt = datetime.strptime(self.timestamp_str, TS_FORMAT)

        self.api_return = {
            "query": {
                "redirects": [{"to": self.expected_title}],
                "pages": {
                    123: {
                        "ns": self.expected_ns,
                        "title": self.expected_title,
                        "revisions": [{"timestamp": self.timestamp_str}],
                    }
                },
            },
        }

        self.le_return = [
            {
                "params": {
                    "target_ns": self.expected_ns,
                    "target_title": self.expected_title,
                },
                "timestamp": time.strptime(self.timestamp_str, TS_FORMAT),
            }
        ]

        self.le_multi = [
            {
                "params": {
                    "target_ns": self.expected_ns,
                    "target_title": self.expected_title,
                },
                "timestamp": time.strptime(self.timestamp_str, TS_FORMAT),
            },
            {
                "params": {
                    "target_ns": self.expected_ns + 10,
                    "target_title": "Some other article",
                },
                "timestamp": time.strptime("2010-08-08T12:30:00Z", TS_FORMAT),
            },
            {
                "params": {
                    "target_ns": self.expected_ns + 20,
                    "target_title": "Another crazy article",
                },
                "timestamp": time.strptime("2008-08-08T12:30:00Z", TS_FORMAT),
            },
        ]

    @patch("wp1.logic.api.page.site")
    def test_no_redirect_no_move(self, unused_patched_site):
        move_data = logic_page.get_move_data(
            self.wp10db, self.wikidb, 0, b"Some Moved Article", datetime(1970, 1, 1)
        )
        self.assertIsNone(move_data)

    @patch("wp1.logic.api.page.site")
    def test_get_redirect_from_api(self, patched_site):
        patched_site.api.side_effect = lambda *args, **kwargs: self.api_return
        move_data = logic_page.get_move_data(
            self.wp10db, self.wikidb, 0, b"Some Moved Article", datetime(1970, 1, 1)
        )

        self.assertIsNotNone(move_data)
        self.assertEqual(self.expected_ns, move_data["dest_ns"])
        self.assertEqual(self.expected_title.encode("utf-8"), move_data["dest_title"])
        self.assertEqual(self.expected_dt, move_data["timestamp_dt"])

    @patch("wp1.logic.api.page.site")
    def test_get_single_move_from_api(self, patched_site):
        patched_site.logevents.side_effect = lambda *args, **kwargs: self.le_return
        move_data = logic_page.get_move_data(
            self.wp10db, self.wikidb, 0, b"Some Moved Article", datetime(1970, 1, 1)
        )

        self.assertIsNotNone(move_data)
        self.assertEqual(self.expected_ns, move_data["dest_ns"])
        self.assertEqual(self.expected_title.encode("utf-8"), move_data["dest_title"])
        self.assertEqual(self.expected_dt, move_data["timestamp_dt"])

    @patch("wp1.logic.api.page.site")
    def test_get_most_recent_move_from_api(self, patched_site):
        patched_site.logevents.side_effect = lambda *args, **kwargs: self.le_multi
        move_data = logic_page.get_move_data(
            self.wp10db, self.wikidb, 0, b"Some Moved Article", datetime(1970, 1, 1)
        )

        self.assertIsNotNone(move_data)
        self.assertEqual(self.expected_ns, move_data["dest_ns"])
        self.assertEqual(self.expected_title.encode("utf-8"), move_data["dest_title"])
        self.assertEqual(self.expected_dt, move_data["timestamp_dt"])

    @patch("wp1.logic.api.page.site")
    def test_get_redirect_too_old_from_api(self, patched_site):
        patched_site.api.side_effect = lambda *args, **kwargs: self.api_return
        move_data = logic_page.get_move_data(
            self.wp10db, self.wikidb, 0, b"Some Moved Article", datetime(2014, 1, 1)
        )
        self.assertIsNone(move_data)

    @patch("wp1.logic.api.page.site")
    def test_get_single_move_too_old_from_api(self, patched_site):
        patched_site.logevents.side_effect = lambda *args, **kwargs: self.le_return
        move_data = logic_page.get_move_data(
            self.wp10db, self.wikidb, 0, b"Some Moved Article", datetime(2014, 1, 1)
        )
        self.assertIsNone(move_data)


class LogicPageMoveDbTest(BaseWpOneDbTest):

    def setUp(self):
        super().setUp()
        self.project = Project(p_project=b"Testing", p_timestamp="201001010000")
        logic_project.insert_or_update(self.wp10db, self.project)

        self.old_ns = 0
        self.old_article = b"The history of testing"
        self.new_ns = 0
        self.new_article = b"History of testing"
        self.dt = datetime(2015, 4, 1)
        self.timestamp_db = self.dt.strftime(TS_FORMAT).encode("utf-8")

    def test_new_move(self):
        logic_page.update_page_moved(
            self.wp10db,
            self.redis,
            self.project,
            self.old_ns,
            self.old_article,
            self.new_ns,
            self.new_article,
            self.dt,
        )

        with self.wp10db.cursor() as cursor:
            cursor.execute(
                """
          SELECT * FROM moves
          WHERE m_old_article = %(old_article)s
      """,
                {"old_article": self.old_article},
            )
            move = Move(**cursor.fetchone())

        self.assertIsNotNone(move)
        self.assertEqual(self.old_ns, move.m_old_namespace)
        self.assertEqual(self.old_article, move.m_old_article)
        self.assertEqual(self.new_ns, move.m_new_namespace)
        self.assertEqual(self.new_article, move.m_new_article)
        self.assertEqual(self.timestamp_db, move.m_timestamp)

    def test_new_move_log(self):
        logic_page.update_page_moved(
            self.wp10db,
            self.redis,
            self.project,
            self.old_ns,
            self.old_article,
            self.new_ns,
            self.new_article,
            self.dt,
        )

        logs = logic_log.get_logs(self.redis, article=self.old_article)
        self.assertEqual(len(logs), 1)
        log = logs[0]

        self.assertIsNotNone(log)
        self.assertEqual(self.old_ns, log.l_namespace)
        self.assertEqual(self.old_article, log.l_article)
        self.assertEqual(b"moved", log.l_action)
        self.assertEqual(b"", log.l_old)
        self.assertEqual(b"", log.l_new)
        self.assertEqual(self.timestamp_db, log.l_revision_timestamp)

    def test_does_not_add_existing_move(self):
        logic_page.update_page_moved(
            self.wp10db,
            self.redis,
            self.project,
            self.old_ns,
            self.old_article,
            self.new_ns,
            self.new_article,
            self.dt,
        )

        logic_page.update_page_moved(
            self.wp10db,
            self.redis,
            self.project,
            self.old_ns,
            self.old_article,
            self.new_ns,
            self.new_article,
            self.dt,
        )

        all_moves = get_all_moves(self.wp10db)
        self.assertEqual(1, len(all_moves))

    def test_does_not_add_existing_log(self):
        logic_page.update_page_moved(
            self.wp10db,
            self.redis,
            self.project,
            self.old_ns,
            self.old_article,
            self.new_ns,
            self.new_article,
            self.dt,
        )

        logic_page.update_page_moved(
            self.wp10db,
            self.redis,
            self.project,
            self.old_ns,
            self.old_article,
            self.new_ns,
            self.new_article,
            self.dt,
        )

        all_logs = get_all_logs(self.redis)
        self.assertEqual(1, len(all_logs))
