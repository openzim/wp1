import unittest
from unittest.mock import patch, ANY

from wp1.web.app import create_app
from wp1.web.base_web_testcase import BaseWebTestcase


class ProjectTest(BaseWebTestcase):

  USER = {
      'access_token': 'access_token',
      'identity': {
          'username': 'WP1_user',
          'sub': '1234'
      }
  }
  invalid_article_names = "Eiffel_Tower\nStatue of#Liberty"
  unsuccessful_response = {
      "success": False,
      "items": {
          'valid': ['Eiffel_Tower'],
          'invalid': ['Statue_of#Liberty'],
          'forbiden_chars': ['#']
      }
  }
  valid_article_names = "Eiffel_Tower\nStatue of Liberty"
  successful_response = {"success": True, "items": {}}

  def test_create_unsuccessful(self):
    self.app = create_app()
    with self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/selection/simple',
                       json={
                           'articles': self.invalid_article_names,
                           'list_name': 'my_list',
                           'project': 'my_project'
                       })
      self.assertEqual(rv.get_json(), self.unsuccessful_response)

  def test_create_successful(self):
    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/selection/simple',
                       json={
                           'articles': self.valid_article_names,
                           'list_name': 'my_list',
                           'project': 'my_project'
                       })
      self.assertEqual(rv.get_json(), self.successful_response)

  @patch('wp1.web.selection.logic_selection')
  def test_create_calls_persist(self, mock_selection):
    expected_articles = ['Eiffel_Tower', 'Statue_of_Liberty']
    mock_selection.validate_list.return_value = (expected_articles, [], [])
    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/selection/simple',
                       json={
                           'articles': self.valid_article_names,
                           'list_name': 'my_list',
                           'project': 'my_project'
                       })
      mock_selection.persist_simple_list.assert_called_once_with(
          ANY, ANY, 'my_list', '1234', 'my_project', expected_articles)

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
                           'articles': self.valid_article_names,
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
                           'articles': self.valid_article_names,
                           'list_name': 'my_list',
                           'project': ''
                       })
      self.assertEqual(rv.status, '400 BAD REQUEST')

  def test_selection_unauthorized_user(self):
    self.app = create_app()
    with self.app.test_client() as client:
      rv = client.post('/v1/selection/simple',
                       json={
                           'articles': self.valid_article_names,
                           'list_name': 'my_list',
                           'project': ''
                       })
    self.assertEqual('401 UNAUTHORIZED', rv.status)
