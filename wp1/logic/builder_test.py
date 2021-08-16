import attr
import datetime
from unittest.mock import patch
from wp1.logic.builder import get_lists, save_builder, insert_builder
from wp1.models.wp10.builder import Builder
from wp1.base_db_test import BaseWpOneDbTest


class BuilderDbUpdateTest(BaseWpOneDbTest):

  builder = Builder(
      b_name='My Builder',
      b_user_id=1234,
      b_project='en.wikipedia.fake',
      b_model='wp1.selection.models.simple',
      b_params='{"list": ["a", "b", "c"]}',
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
      'b_created_at': b'20191225044444\x00\x00\x00\x00\x00\x00',
      'b_updated_at': b'20191225044444\x00\x00\x00\x00\x00\x00',
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

  def _get_builder_by_user_id(self):
    with self.wp10db.cursor() as cursor:
      cursor.execute('SELECT * FROM builders WHERE b_user_id=%(b_user_id)s',
                     {'b_user_id': '1234'})
      article_data = cursor.fetchone()
      return article_data

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_save_builder(self, mock_utcnow):
    save_builder(self.wp10db, 'My Builder', '1234', 'en.wikipedia.fake',
                 'a\nb\nc')
    article_data = self._get_builder_by_user_id()
    self.assertEqual(self.expected_builder, article_data)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_insert_builder(self, mock_utcnow):
    insert_builder(self.wp10db, self.builder)
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
