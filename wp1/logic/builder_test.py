import datetime
from unittest.mock import patch, MagicMock, ANY

import attr

from wp1.base_db_test import BaseWpOneDbTest
from wp1.logic.builder import save_builder, insert_builder, get_builder, get_lists, materialize_builder
from wp1.models.wp10.builder import Builder
from wp1.selection.models.simple_builder import SimpleBuilder


class BuilderTest(BaseWpOneDbTest):

  builder = Builder(
      b_name=b'My Builder',
      b_user_id=1234,
      b_project=b'en.wikipedia.fake',
      b_model=b'wp1.selection.models.simple',
      b_params=b'{"list": ["a", "b", "c"]}',
      b_created_at=b'20191225044444',
      b_updated_at=b'20191225044444',
  )

  expected_builder = {
      'b_id': 1,
      'b_name': b'My Builder',
      'b_user_id': 1234,
      'b_project': b'en.wikipedia.fake',
      'b_model': b'wp1.selection.models.simple',
      'b_params': b'{"list": ["a", "b", "c"]}',
      'b_created_at': b'20191225044444',
      'b_updated_at': b'20191225044444',
  }

  expected_lists = [{
      'id':
          1,
      'name':
          'My Builder',
      'project':
          'en.wikipedia.fake',
      'selections': [{
          's_id': '1',
          'content_type': 'tsv',
          'selection_url': 'https://www.example.com/<id>'
      }]
  }]

  expected_lists_with_multiple_selections = [{
      'id':
          1,
      'name':
          'My Builder',
      'project':
          'en.wikipedia.fake',
      'selections': [{
          's_id': '1',
          'content_type': 'tsv',
          'selection_url': 'https://www.example.com/<id>'
      }, {
          's_id': '2',
          'content_type': 'xls',
          'selection_url': 'https://www.example.com/<id>'
      }]
  }]

  expected_lists_with_no_selections = [{
      'id': 1,
      'name': 'My Builder',
      'project': 'en.wikipedia.fake',
      'selections': []
  }]

  def _insert_builder(self):
    with self.wp10db.cursor() as cursor:
      cursor.execute(
          '''INSERT INTO builders
         (b_name, b_user_id, b_project, b_params, b_model, b_created_at, b_updated_at)
         VALUES (%(b_name)s, %(b_user_id)s, %(b_project)s, %(b_params)s, %(b_model)s, %(b_created_at)s, %(b_updated_at)s)
        ''', attr.asdict(self.builder))
      id_ = cursor.lastrowid
    self.wp10db.commit()
    return id_

  def _get_builder_by_user_id(self):
    with self.wp10db.cursor() as cursor:
      cursor.execute('SELECT * FROM builders WHERE b_user_id=%(b_user_id)s',
                     {'b_user_id': '1234'})
      db_lists = cursor.fetchone()
      return db_lists

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_save_builder(self, mock_utcnow):
    save_builder(self.wp10db, 'My Builder', '1234', 'en.wikipedia.fake',
                 'a\nb\nc')
    db_lists = self._get_builder_by_user_id()
    self.assertEqual(self.expected_builder, db_lists)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_insert_builder(self, mock_utcnow):
    insert_builder(self.wp10db, self.builder)
    db_lists = self._get_builder_by_user_id()
    self.assertEqual(self.expected, db_lists)

  def test_get_builder(self):
    id_ = self._insert_builder()

    actual = get_builder(self.wp10db, id_)
    self.builder.b_id = id_
    self.assertEqual(self.builder, actual)

  @patch('wp1.logic.builder.wp10_connect')
  @patch('wp1.logic.builder.connect_storage')
  def test_materialize(self, patched_connect_storage, patched_connect_wp10):
    patched_connect_wp10.return_value = self.wp10db
    TestBuilderClass = MagicMock()
    materialize_mock = MagicMock()
    TestBuilderClass.return_value = materialize_mock

    orig_close = self.wp10db.close
    try:
      self.wp10db.close = lambda: True
      id_ = self._insert_builder()

      materialize_builder(TestBuilderClass, id_, 'text/tab-separated-values')
      materialize_mock.materialize.assert_called_once_with(
          ANY, ANY, self.builder, 'text/tab-separated-values')
    finally:
      self.wp10db.close = orig_close
    article_data = self._get_builder_by_user_id()
    self.assertEqual(self.expected_builder, article_data)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_get_lists(self, mock_utcnow):
    with self.wp10db.cursor() as cursor:
      cursor.execute(
          '''INSERT INTO selections VALUES (1, 1, 'tsv', '20191225044444')''')
      cursor.execute(
          '''INSERT INTO builders
        (b_name, b_user_id, b_project, b_params, b_model, b_created_at, b_updated_at)
        VALUES (%(b_name)s, %(b_user_id)s, %(b_project)s,
                %(b_params)s, %(b_model)s, %(b_created_at)s, %(b_updated_at)s)
      ''', attr.asdict(self.builder))
    article_data = get_lists(self.wp10db, '1234')
    self.assertEqual(self.expected_lists, article_data)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_get_lists_with_multiple_selections(self, mock_utcnow):
    with self.wp10db.cursor() as cursor:
      cursor.execute(
          '''INSERT INTO selections VALUES (1, 1, 'tsv', '20191225044444')''')
      cursor.execute(
          '''INSERT INTO selections VALUES (2, 1, "xls", '20201225105544')''')
      cursor.execute(
          '''INSERT INTO builders
        (b_name, b_user_id, b_project, b_params,
         b_model, b_created_at, b_updated_at)
        VALUES (%(b_name)s, %(b_user_id)s, %(b_project)s,
                %(b_params)s, %(b_model)s, %(b_created_at)s, %(b_updated_at)s)
      ''', attr.asdict(self.builder))
    article_data = get_lists(self.wp10db, '1234')
    self.assertEqual(self.expected_lists_with_multiple_selections, article_data)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_get_lists_with_no_selections(self, mock_utcnow):
    with self.wp10db.cursor() as cursor:
      cursor.execute(
          '''INSERT INTO builders
        (b_name, b_user_id, b_project, b_params,
         b_model, b_created_at, b_updated_at)
        VALUES (%(b_name)s, %(b_user_id)s, %(b_project)s,
                %(b_params)s, %(b_model)s, %(b_created_at)s, %(b_updated_at)s)
      ''', attr.asdict(self.builder))
    article_data = get_lists(self.wp10db, '1234')
    self.assertEqual(self.expected_lists_with_no_selections, article_data)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_get_empty_lists(self, mock_utcnow):
    with self.wp10db.cursor() as cursor:
      cursor.execute(
          '''INSERT INTO selections VALUES (1, 1, 'tsv', '20191225044444')''')
      cursor.execute(
          '''INSERT INTO builders
        (b_name, b_user_id, b_project, b_params, b_model, b_created_at, b_updated_at)
        VALUES (%(b_name)s, %(b_user_id)s, %(b_project)s, %(b_params)s,
                %(b_model)s, %(b_created_at)s, %(b_updated_at)s)
      ''', attr.asdict(self.builder))
    article_data = get_lists(self.wp10db, '0000')
    self.assertEqual([], article_data)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_get_lists_with_no_builders(self, mock_utcnow):
    with self.wp10db.cursor() as cursor:
      cursor.execute(
          '''INSERT INTO selections VALUES (1, 1, 'tsv', '20191225044444')''')
    article_data = get_lists(self.wp10db, '0000')
    self.assertEqual([], article_data)
