from unittest.mock import patch

import attr

from wp1.models.wp10.builder import Builder
from wp1.web.app import create_app
from wp1.web.base_web_testcase import BaseWebTestcase


class BuildersTest(BaseWebTestcase):
  USER = {
      'access_token': 'access_token',
      'identity': {
          'username': 'WP1_user',
          'sub': 1234,
      },
  }
  invalid_article_name = 'Eiffel_Tower\nStatue of#Liberty'
  unsuccessful_response = {
      'success': False,
      'items': {
          'valid': ['Eiffel_Tower'],
          'invalid': ['Statue_of#Liberty'],
          'errors': ['The list contained the following invalid characters: #'],
      },
  }
  valid_article_name = 'Eiffel_Tower\nStatue of Liberty'
  successful_response = {'success': True, 'items': {}}

  builder = Builder(
      b_name=b'My Builder',
      b_user_id=1234,
      b_project=b'en.wikipedia.fake',
      b_model=b'wp1.selection.models.simple',
      b_params=b'{"list": ["a", "b", "c"]}',
      b_created_at=b'20191225044444',
      b_updated_at=b'20191225044444',
  )

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

  def test_create_unsuccessful(self):
    self.app = create_app()
    with self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/',
                       json={
                           'articles': self.invalid_article_name,
                           'name': 'my_list',
                           'project': 'my_project'
                       })
      self.assertEqual(self.unsuccessful_response, rv.get_json())

  def test_create_successful(self):
    self.app = create_app()
    with self.app.test_client() as client, self.override_db(self.app):
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/',
                       json={
                           'articles': self.valid_article_name,
                           'name': 'my_list',
                           'project': 'my_project'
                       })
      self.assertEqual(self.successful_response, rv.get_json())

  def test_update_unsuccessful(self):
    builder_id = self._insert_builder()
    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/%s' % builder_id,
                       json={
                           'articles': self.invalid_article_name,
                           'name': 'updated_list',
                           'project': 'my_project'
                       })
      self.assertEqual(self.unsuccessful_response, rv.get_json())

  def test_update_successful(self):
    builder_id = self._insert_builder()
    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/%s' % builder_id,
                       json={
                           'articles': self.valid_article_name,
                           'name': 'updated_list',
                           'project': 'my_project'
                       })
      print(rv.status)
      self.assertEqual(self.successful_response, rv.get_json())

  def test_update_not_owner(self):
    builder_id = self._insert_builder()
    different_user = {
        'access_token': 'access_token',
        'identity': {
            'username': 'Another_User',
            'sub': 5555,
        },
    }
    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = different_user
      rv = client.post('/v1/builders/%s' % builder_id,
                       json={
                           'articles': self.valid_article_name,
                           'name': 'updated_list',
                           'project': 'my_project'
                       })
      self.assertEqual('404 NOT FOUND', rv.status)

  def test_empty_article_create(self):
    self.app = create_app()
    with self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/',
                       json={
                           'articles': '',
                           'name': 'my_list',
                           'project': 'my_project'
                       })
      self.assertEqual('400 BAD REQUEST', rv.status)

  def test_empty_list_create(self):
    self.app = create_app()
    with self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/',
                       json={
                           'articles': self.valid_article_name,
                           'name': '',
                           'project': 'my_project'
                       })
      self.assertEqual('400 BAD REQUEST', rv.status)

  def test_empty_project_create(self):
    self.app = create_app()
    with self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/',
                       json={
                           'articles': self.valid_article_name,
                           'name': 'my_list',
                           'project': ''
                       })
      self.assertEqual('400 BAD REQUEST', rv.status)

  def test_selection_unauthorized_user_create(self):
    self.app = create_app()
    with self.app.test_client() as client:
      rv = client.post('/v1/builders/',
                       json={
                           'articles': self.valid_article_name,
                           'name': 'my_list',
                           'project': 'my_project'
                       })
    self.assertEqual('401 UNAUTHORIZED', rv.status)

  def test_empty_article_update(self):
    builder_id = self._insert_builder()
    self.app = create_app()
    with self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/%s' % builder_id,
                       json={
                           'articles': '',
                           'name': 'my_list',
                           'project': 'my_project'
                       })
      self.assertEqual('400 BAD REQUEST', rv.status)

  def test_empty_list_update(self):
    builder_id = self._insert_builder()
    self.app = create_app()
    with self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/%s' % builder_id,
                       json={
                           'articles': self.valid_article_name,
                           'name': '',
                           'project': 'my_project'
                       })
      self.assertEqual('400 BAD REQUEST', rv.status)

  def test_empty_project_update(self):
    builder_id = self._insert_builder()
    self.app = create_app()
    with self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/%s' % builder_id,
                       json={
                           'articles': self.valid_article_name,
                           'name': 'my_list',
                           'project': ''
                       })
      self.assertEqual('400 BAD REQUEST', rv.status)

  def test_selection_unauthorized_user_update(self):
    builder_id = self._insert_builder()
    self.app = create_app()
    with self.app.test_client() as client:
      rv = client.post('/v1/builders/%s' % builder_id,
                       json={
                           'articles': self.valid_article_name,
                           'name': 'my_list',
                           'project': 'my_project'
                       })
    self.assertEqual('401 UNAUTHORIZED', rv.status)
