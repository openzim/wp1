from unittest.mock import patch
from wp1.logic.builder import save_builder, insert_builder
from wp1.models.wp10.builder import Builder
from wp1.base_db_test import BaseWpOneDbTest


class BuilderDbUpdateTest(BaseWpOneDbTest):

  builder = Builder(b_name='My Builder',
                    b_user_id=1234,
                    b_project='en.wikipedia.fake',
                    b_model='wp1.selection.models.simple',
                    b_params='{"list": ["a", "b", "c"]}')

  expected = {
      'b_id': 1,
      'b_name': b'My Builder',
      'b_user_id': 1234,
      'b_project': b'en.wikipedia.fake',
      'b_model': b'wp1.selection.models.simple',
      'b_params': b'{"list": ["a", "b", "c"]}',
      'b_created_at': None,
      'b_updated_at': None
  }

  @patch('wp1.models.wp10.builder.utcnow', return_value=None)
  def test_save_builder(self, mock_utcnow):
    save_builder(self.wp10db, 'My Builder', '1234', 'en.wikipedia.fake',
                 'a\nb\nc')
    with self.wp10db.cursor() as cursor:
      cursor.execute('SELECT * FROM builders WHERE b_user_id=%(b_user_id)s',
                     {'b_user_id': '1234'})
      db_lists = cursor.fetchone()
    self.assertEqual(self.expected, db_lists)

  def test_insert_builder(self):
    insert_builder(self.wp10db, self.builder)
    with self.wp10db.cursor() as cursor:
      cursor.execute('SELECT * FROM builders WHERE b_user_id=%(b_user_id)s',
                     {'b_user_id': '1234'})
      db_lists = cursor.fetchone()
    self.assertEqual(self.expected, db_lists)
