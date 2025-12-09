from contextlib import contextmanager
import unittest
from unittest.mock import MagicMock

from flask import appcontext_pushed, g
import fakeredis
import pymysql

from wp1.base_db_test import BaseCombinedDbTest
from wp1.web.app import create_app


class BaseWebTestcase(BaseCombinedDbTest):

    def setUp(self):
        super().setUp()

        self.redis = fakeredis.FakeStrictRedis()

        self.app = create_app()
        self.app.config["TESTING"] = True

    @contextmanager
    def override_db(self, app):

        @contextmanager
        def set_wiki_db():

            def handler(sender, **kwargs):
                g.wikidb = self.connect_wiki_db()

            with appcontext_pushed.connected_to(handler, app):
                yield

        @contextmanager
        def set_wp10_db():

            def handler(sender, **kwargs):
                g.wp10db = self.connect_wp_one_db()

            with appcontext_pushed.connected_to(handler, app):
                yield

        @contextmanager
        def set_redis():

            def handler(sender, **kwargs):
                g.redis = self.redis

            with appcontext_pushed.connected_to(handler, app):
                yield

        @contextmanager
        def set_storage():

            def handler(sender, **kwargs):
                g.storage = MagicMock()

            with appcontext_pushed.connected_to(handler, app):
                yield

        with set_wiki_db(), set_wp10_db(), set_redis(), set_storage():
            yield
