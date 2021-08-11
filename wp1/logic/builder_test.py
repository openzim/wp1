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

  expected = {
      's_id': 1,
      's_builder_id': 1,
      's_content_type': 'tsv',
      's_updated_at': b'20191225044444\x00\x00\x00\x00\x00\x00',
      'b_id': 1,
      'b_name': b'My Builder',
      'b_user_id': 1234,
      'b_project': b'en.wikipedia.fake',
      'b_model': b'wp1.selection.models.simple',
      'b_params': b'{"list": ["a", "b", "c"]}',
      'b_created_at': b'20191225044444\x00\x00\x00\x00\x00\x00',
      'b_updated_at': b'20191225044444\x00\x00\x00\x00\x00\x00',
  }

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
    self.assertEqual(self.expected, db_lists)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_insert_builder(self, mock_utcnow):
    insert_builder(self.wp10db, self.builder)
    db_lists = self._get_builder_by_user_id()
    self.assertEqual(self.expected, db_lists)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_get_lists(self, mock_utcnow):
    save_builder(self.wp10db, 'My Builder', '1234', 'en.wikipedia.fake',
                 'a\nb\nc')
    with self.wp10db.cursor() as cursor:
      cursor.execute(
          '''INSERT INTO selections VALUES (1, 1, 'tsv', b'20191225044444')''')
    db_lists = get_lists(self.wp10db, '1234')
    self.assertEqual([self.expected], db_lists)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_get_empty_lists(self, mock_utcnow):
    save_builder(self.wp10db, 'My Builder', '1234', 'en.wikipedia.fake',
                 'a\nb\nc')
    with self.wp10db.cursor() as cursor:
      cursor.execute(
          '''INSERT INTO selections VALUES (1, 1, "tsv", b'20191225044444')''')
    db_lists = get_lists(self.wp10db, '0000')
    self.assertEqual(None, db_lists)
