from contextlib import contextmanager
import unittest
from unittest.mock import MagicMock, patch

from flask import appcontext_pushed, g
from flask.testing import FlaskClient
import fakeredis
import pymysql

from wp1.base_db_test import BaseCombinedDbTest
from wp1.web.app import create_app


class FrontendTestClient(FlaskClient):
    """Existing web tests model requests from the configured frontend."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.environ_base["HTTP_ORIGIN"] = next(
            iter(self.application.config["TRUSTED_CLIENT_ORIGINS"])
        )


class BaseWebTestcase(BaseCombinedDbTest):

    def setUp(self):
        super().setUp()

        self.redis = fakeredis.FakeStrictRedis()
        client_patch = patch("flask.Flask.test_client_class", FrontendTestClient)
        client_patch.start()
        self.addCleanup(client_patch.stop)

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
