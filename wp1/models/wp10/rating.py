from datetime import datetime
import logging
import urllib.parse

import attr

from wp1.constants import TS_FORMAT, FRONTEND_WIKI_BASE
import wp1.logic.util as logic_util

logger = logging.getLogger(__name__)


@attr.s
class Rating:
    table_name = "ratings"

    r_project = attr.ib()
    r_namespace = attr.ib()
    r_article = attr.ib()
    r_score = attr.ib(default=0)
    r_quality = attr.ib(default=None)
    r_quality_timestamp = attr.ib(default=None)
    r_importance = attr.ib(default=None)
    r_importance_timestamp = attr.ib(default=None)

    # The timestamp parsed into a datetime.datetime object.
    @property
    def quality_timestamp_dt(self):
        return datetime.strptime(self.r_quality_timestamp.decode("utf-8"), TS_FORMAT)

    @property
    def importance_timestamp_dt(self):
        return datetime.strptime(self.r_importance_timestamp.decode("utf-8"), TS_FORMAT)

    def set_quality_timestamp_dt(self, dt):
        """Sets the quality_timestamp field using a datetime.datetime object"""
        if dt is None:
            logger.warning("Attempt to set rating quality_timestamp to None ignored")
            return
        self.r_quality_timestamp = dt.strftime(TS_FORMAT).encode("utf-8")

    def set_importance_timestamp_dt(self, dt):
        """Sets the quality_timestamp field using a datetime.datetime object"""
        if dt is None:
            logger.warning("Attempt to set rating importance_timestamp to None ignored")
            return
        self.r_importance_timestamp = dt.strftime(TS_FORMAT).encode("utf-8")

    def _get_namespace_prefix(self, wp10db, ns=None):
        if ns is None:
            ns = self.r_namespace
        namespace_prefix = ""
        if ns != 0:
            base_prefix = logic_util.int_to_ns(wp10db)[ns]
            namespace_prefix = base_prefix.decode("utf-8") + ":"
        return namespace_prefix

    def _make_article_link(self, wp10db, article_name):
        namespace_prefix = self._get_namespace_prefix(wp10db)

        return "%sindex.php?title=%s%s" % (
            FRONTEND_WIKI_BASE,
            namespace_prefix,
            urllib.parse.quote(article_name),
        )

    def _make_article_talk_link(self, wp10db, article_name):
        namespace_prefix = self._get_namespace_prefix(wp10db, self.r_namespace + 1)

        return "%sindex.php?title=%s%s" % (
            FRONTEND_WIKI_BASE,
            namespace_prefix,
            urllib.parse.quote(article_name),
        )

    def _make_article_history_link(self, wp10db, article_name):
        return "%s&action=history" % self._make_article_link(wp10db, article_name)

    def to_web_dict(self, wp10db):
        namespace_prefix = self._get_namespace_prefix(wp10db)
        talk_prefix = self._get_namespace_prefix(wp10db, self.r_namespace + 1)
        article_name = self.r_article.decode("utf-8").replace("_", " ")
        return {
            "article": "%s%s" % (namespace_prefix, article_name),
            "article_talk": "%s%s" % (talk_prefix, article_name),
            "article_link": self._make_article_link(wp10db, article_name),
            "article_talk_link": self._make_article_talk_link(wp10db, article_name),
            "article_history_link": self._make_article_history_link(
                wp10db, article_name
            ),
            "quality": self.r_quality.decode("utf-8"),
            "quality_updated": (
                self.r_quality_timestamp.decode("utf-8")
                if self.r_quality_timestamp
                else None
            ),
            "importance": self.r_importance.decode("utf-8"),
            "importance_updated": (
                self.r_importance_timestamp.decode("utf-8")
                if self.r_importance_timestamp
                else None
            ),
        }
