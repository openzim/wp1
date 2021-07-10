from contextlib import contextmanager
import unittest
from unittest.mock import MagicMock

from flask import appcontext_pushed, g
import fakeredis
import pymysql

from wp1.base_db_test import parse_sql
from wp1.web.app import create_app


class BaseWebTestcase(unittest.TestCase):

  def _connect_wp_one_db(self):
    return pymysql.connect(host='localhost',
                           db='enwp10_test',
                           user='root',
                           charset=None,
                           use_unicode=False,
                           cursorclass=pymysql.cursors.DictCursor)

  def _connect_wiki_db(self):
    return pymysql.connect(host='localhost',
                           db='enwikip_test',
                           user='root',
                           charset=None,
                           use_unicode=False,
                           cursorclass=pymysql.cursors.DictCursor)

  def _cleanup_wp_one_db(self):
    stmts = parse_sql('wp10_test.down.sql')
    with self.wp10db.cursor() as cursor:
      for stmt in stmts:
        cursor.execute(stmt)
    self.wp10db.commit()
    self.wp10db.close()

  def _setup_wp_one_db(self):
    self.wp10db = self._connect_wp_one_db()
    stmts = parse_sql('wp10_test.up.sql')
    with self.wp10db.cursor() as cursor:
      for stmt in stmts:
        cursor.execute(stmt)
    self.wp10db.commit()

  def _cleanup_wiki_db(self):
    stmts = parse_sql('wiki_test.down.sql')
    with self.wikidb.cursor() as cursor:
      for stmt in stmts:
        cursor.execute(stmt)
    self.wikidb.commit()
    self.wikidb.close()

  def _setup_wiki_db(self):
    self.wikidb = self._connect_wiki_db()
    stmts = parse_sql('wiki_test.up.sql')
    with self.wikidb.cursor() as cursor:
      for stmt in stmts:
        cursor.execute(stmt)
    self.wikidb.commit()

  def setUp(self):
    self.addCleanup(self._cleanup_wiki_db)
    self._setup_wiki_db()

    self.addCleanup(self._cleanup_wp_one_db)
    self._setup_wp_one_db()

    self.redis = fakeredis.FakeStrictRedis()

    self.app = create_app()
    self.app.config['TESTING'] = True

  @contextmanager
  def override_db(self, app):

    @contextmanager
    def set_wiki_db():

      def handler(sender, **kwargs):
        g.wikidb = self._connect_wiki_db()

      with appcontext_pushed.connected_to(handler, app):
        yield

    @contextmanager
    def set_wp10_db():

      def handler(sender, **kwargs):
        g.wp10db = self._connect_wp_one_db()

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
        mock_storage = MagicMock()
        mock_storage.bucket_name.encode = MagicMock(
            return_value=b'test-bucket-name')
        mock_storage.region.encode = MagicMock(return_value=b'test-region')
        g.storage = mock_storage

      with appcontext_pushed.connected_to(handler, app):
        yield

    with set_wiki_db(), set_wp10_db(), set_redis(), set_storage():
      yield
