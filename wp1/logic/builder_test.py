from unittest.mock import patch
from wp1.logic.builder import generate_builder, insert_builder
from wp1.models.wp10.builder import Builder
from wp1.web.base_web_testcase import BaseWebTestcase


class BuilderDbUpdateTest(BaseWebTestcase):

  USER = {
      'access_token': 'access_token',
      'identity': {
          'username': 'WP1_user',
          'sub': '1234'
      }
  }

  builder = Builder(b_name='My Builder',
                    b_user_id=1234,
                    b_project='en.wikipedia.fake',
                    b_model='wp1.selection.models.simple',
                    b_params="{'list': ['a', 'b', 'c']}")

  expected = {
      'b_id': 1,
      'b_name': b'My Builder',
      'b_user_id': 1234,
      'b_project': b'en.wikipedia.fake',
      'b_model': b'wp1.selection.models.simple',
      'b_params': b"{'list': ['a', 'b', 'c']}",
      'b_created_at': None,
      'b_updated_at': None
  }

  def setUp(self):
    super().setUp()

  @patch('wp1.models.wp10.builder.utcnow', return_value=None)
  def test_generate_builder(self, mock_utcnow):
    with self.override_db(self.app):
      data = {
          'articles': 'a\nb\nc',
          'list_name': 'My Builder',
          'project': 'en.wikipedia.fake'
      }
      generate_builder(data, 1234, self.wp10db)
      with self.wp10db.cursor() as cursor:
        cursor.execute('SELECT * FROM builders WHERE b_user_id=%(b_user_id)s',
                       {'b_user_id': '1234'})
        db_lists = cursor.fetchone()
      self.assertEqual(self.expected, db_lists)

  def test_insert_builder(self):
    insert_builder(self.builder, self.wp10db)
    with self.wp10db.cursor() as cursor:
      cursor.execute('SELECT * FROM builders WHERE b_user_id=%(b_user_id)s',
                     {'b_user_id': '1234'})
      db_lists = cursor.fetchone()
    self.assertEqual(self.expected, db_lists)
