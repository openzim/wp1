from unittest.mock import patch
from wp1.web.app import create_app
from wp1.web.base_web_testcase import BaseWebTestcase


class SelectionTest(BaseWebTestcase):

  USER = {
      'access_token': 'access_token',
      'identity': {
          'username': 'WP1_user',
          'sub': '1234'
      }
  }
  invalid_article_name = "Eiffel_Tower\nStatue of#Liberty"
  unsuccessful_response = {
      "success": False,
      "items": {
          'valid': ['Eiffel_Tower'],
          'invalid': ['Statue_of#Liberty'],
          'errors': ['The list contained the following invalid characters: #']
      }
  }
  valid_article_name = "Eiffel_Tower\nStatue of Liberty"
  successful_response = {"success": True, "items": {}}

  expected = {
      'list_data': [{
          'content_type': "tsv",
          'extension': ['tsv'],
          'name': 'list_name',
          'project': 'project_name',
          'url': 'https://www.example.com/<id>',
          'id': 11
      }]
  }

  # def test_create_unsuccessful(self):
  #   self.app = create_app()
  #   with self.app.test_client() as client:
  #     with client.session_transaction() as sess:
  #       sess['user'] = self.USER
  #     rv = client.post('/v1/selection/simple',
  #                      json={
  #                          'articles': self.invalid_article_name,
  #                          'list_name': 'my_list',
  #                          'project': 'my_project'
  #                      })
  #     self.assertEqual(rv.get_json(), self.unsuccessful_response)

  # def test_create_successful(self):
  #   self.app = create_app()
  #   with self.app.test_client() as client, self.override_db(self.app):
  #     with client.session_transaction() as sess:
  #       sess['user'] = self.USER
  #     rv = client.post('/v1/selection/simple',
  #                      json={
  #                          'articles': self.valid_article_name,
  #                          'list_name': 'my_list',
  #                          'project': 'my_project'
  #                      })
  #     self.assertEqual(rv.get_json(), self.successful_response)

  # def test_empty_article(self):
  #   self.app = create_app()
  #   with self.app.test_client() as client:
  #     with client.session_transaction() as sess:
  #       sess['user'] = self.USER
  #     rv = client.post('/v1/selection/simple',
  #                      json={
  #                          'articles': '',
  #                          'list_name': 'my_list',
  #                          'project': 'my_project'
  #                      })
  #     self.assertEqual(rv.status, '400 BAD REQUEST')

  # def test_empty_list(self):
  #   self.app = create_app()
  #   with self.app.test_client() as client:
  #     with client.session_transaction() as sess:
  #       sess['user'] = self.USER
  #     rv = client.post('/v1/selection/simple',
  #                      json={
  #                          'articles': self.valid_article_name,
  #                          'list_name': '',
  #                          'project': 'my_project'
  #                      })
  #     self.assertEqual(rv.status, '400 BAD REQUEST')

  # def test_empty_project(self):
  #   self.app = create_app()
  #   with self.app.test_client() as client:
  #     with client.session_transaction() as sess:
  #       sess['user'] = self.USER
  #     rv = client.post('/v1/selection/simple',
  #                      json={
  #                          'articles': self.valid_article_name,
  #                          'list_name': 'my_list',
  #                          'project': ''
  #                      })
  #     self.assertEqual(rv.status, '400 BAD REQUEST')

  # def test_selection_unauthorized_user(self):
  #   self.app = create_app()
  #   with self.app.test_client() as client:
  #     rv = client.post('/v1/selection/simple',
  #                      json={
  #                          'articles': self.valid_article_name,
  #                          'list_name': 'my_list',
  #                          'project': ''
  #                      })
  #   self.assertEqual('401 UNAUTHORIZED', rv.status)

  @patch('wp1.web.selection.get_lists',
         return_value=[{
             'b_id': 11,
             'b_name': b'list_name',
             'b_project': b'project_name'
         }])
  def test_get_list_data(self, mockes_utcnow):
    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with self.wp10db.cursor() as cursor:
        cursor.execute('''INSERT INTO builders
        (b_name, b_user_id, b_project, b_model)
        VALUES ('list_name', '11', 'project_name', 'model')
      ''')
        cursor.execute(
            '''INSERT INTO selections VALUES (1, 1, "tsv", b'20201225105544')'''
        )
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.get('/v1/selection/simple/lists')
      print(rv.get_json())
      self.assertEqual(rv.get_json(), self.expected)
