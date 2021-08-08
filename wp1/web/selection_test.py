import unittest
from wp1.base_db_test import BaseWpOneDbTest
from wp1.selection.models.simple_builder import SimpleBuilder
from wp1.web.app import create_app


class ProjectTest(unittest.TestCase):

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

  def test_create_unsuccessful(self):
    self.app = create_app()
    with self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/selection/simple',
                       json={
                           'articles': self.invalid_article_name,
                           'list_name': 'my_list',
                           'project': 'my_project'
                       })
      self.assertEqual(rv.get_json(), self.unsuccessful_response)

  def test_create_successful(self):
    self.app = create_app()
    with self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/selection/simple',
                       json={
                           'articles': self.valid_article_name,
                           'list_name': 'my_list',
                           'project': 'my_project'
                       })
      self.assertEqual(rv.get_json(), self.successful_response)

  def test_empty_article(self):
    self.app = create_app()
    with self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/selection/simple',
                       json={
                           'articles': '',
                           'list_name': 'my_list',
                           'project': 'my_project'
                       })
      self.assertEqual(rv.status, '400 BAD REQUEST')

  def test_empty_list(self):
    self.app = create_app()
    with self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/selection/simple',
                       json={
                           'articles': self.valid_article_name,
                           'list_name': '',
                           'project': 'my_project'
                       })
      self.assertEqual(rv.status, '400 BAD REQUEST')

  def test_empty_project(self):
    self.app = create_app()
    with self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/selection/simple',
                       json={
                           'articles': self.valid_article_name,
                           'list_name': 'my_list',
                           'project': ''
                       })
      self.assertEqual(rv.status, '400 BAD REQUEST')

  def test_selection_unauthorized_user(self):
    self.app = create_app()
    with self.app.test_client() as client:
      rv = client.post('/v1/selection/simple',
                       json={
                           'articles': self.valid_article_name,
                           'list_name': 'my_list',
                           'project': ''
                       })
    self.assertEqual('401 UNAUTHORIZED', rv.status)


class BuilderDbUpdateTest(BaseWpOneDbTest):

  data = {
      'articles': 'article1 \narticle2',
      'list_name': 'list_name',
      'project': 'en.wikipedia.org'
  }

  def setUp(self):
    super().setUp()

  def test_get_list_data(self):
    self.app = create_app()
    simple_builder = SimpleBuilder()
    simple_builder.insert_builder(self.data, self.wp10db)
    with self.app.test_client as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.get('/v1/selection/simple/lists')
      print(rv)
    self.asserEqual('', rv.get_json())
