from contextlib import contextmanager
from flask import appcontext_pushed, g

from wp1.base_db_test import BaseCombinedDbTest
from wp1.web.app import app


class BaseWebTestcase(BaseCombinedDbTest):

  def setUp(self):
    super().setUp()
    app.config['TESTING'] = True

  @contextmanager
  def _override_db(self, app):

    @contextmanager
    def set_wiki_db():

      def handler(sender, **kwargs):
        g.wikidb = self.wikidb

      with appcontext_pushed.connected_to(handler, app):
        yield

    @contextmanager
    def set_wp10_db():

      def handler(sender, **kwargs):
        g.wp10db = self.wp10db

      with appcontext_pushed.connected_to(handler, app):
        yield

    with set_wiki_db(), set_wp10_db():
      yield
