import datetime
from unittest.mock import patch

import attr

from wp1.exceptions import ObjectNotFoundError, UserNotAuthorizedError, ZimFarmError
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
  UNAUTHORIZED_USER = {
      'access_token': 'access_token',
      'identity': {
          'username': 'WP1_user_2',
          'sub': 5678,
      },
  }
  invalid_article_name = ['Eiffel_Tower', 'Statue of#Liberty']
  unsuccessful_response = {
      'success': False,
      'items': {
          'valid': ['Eiffel_Tower'],
          'invalid': ['Statue_of#Liberty'],
          'errors': ['The list contained the following invalid characters: #'],
      },
  }
  empty_response = {
      'success': False,
      'items': {
          'valid': [],
          'invalid': [],
          'errors': ['Empty List'],
      },
  }
  valid_article_name = ['Eiffel_Tower', 'Statue of Liberty']
  successful_response = {'success': True, 'items': {}}

  builder = Builder(b_id=b'1a-2b-3c-4d',
                    b_name=b'My Builder',
                    b_user_id=1234,
                    b_project=b'en.wikipedia.fake',
                    b_model=b'wp1.selection.models.simple',
                    b_params=b'{"list": ["a", "b", "c"]}',
                    b_created_at=b'20191225044444',
                    b_updated_at=b'20191225044444',
                    b_current_version=2,
                    b_selection_zim_version=2)

  def _insert_builder(self):
    with self.wp10db.cursor() as cursor:
      cursor.execute(
          '''INSERT INTO builders
               (b_id, b_name, b_user_id, b_project, b_params, b_model,
                b_created_at, b_updated_at, b_current_version,
                b_selection_zim_version)
             VALUES
               (%(b_id)s, %(b_name)s, %(b_user_id)s, %(b_project)s,
                %(b_params)s, %(b_model)s, %(b_created_at)s,
                %(b_updated_at)s, %(b_current_version)s, %(b_selection_zim_version)s)
        ''', attr.asdict(self.builder))
    self.wp10db.commit()
    return self.builder.b_id.decode('utf-8')

  def _insert_selections(self, builder_id):
    selections = [(1, builder_id, 'text/tab-separated-values', '20201225105544',
                   1, 'object_key1'),
                  (2, builder_id, 'application/vnd.ms-excel', '20201225105544',
                   1, 'object_key2'),
                  (3, builder_id, 'text/tab-separated-values', '20201225105544',
                   2, 'latest_object_key_tsv', 'task-id-1234', 'FILE_READY'),
                  (4, builder_id, 'application/vnd.ms-excel', '20201225105544',
                   2, 'latest_object_key_xls')]
    with self.wp10db.cursor() as cursor:
      cursor.executemany(
          '''INSERT INTO selections
               (s_id, s_builder_id, s_content_type, s_updated_at,
                s_version, s_object_key)
             VALUES (%s, %s, %s, %s, %s, %s)
      ''', [s[:6] for s in selections])
      cursor.execute(
          '''INSERT INTO zim_files
               (z_id, z_selection_id, z_task_id, z_status)
             VALUES
               (1, %s, %s, %s)''', (
              selections[2][0],
              selections[2][6],
              selections[2][7],
          ))
    self.wp10db.commit()

  def test_create_unsuccessful(self):
    self.app = create_app()
    with self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/',
                       json={
                           'model': 'wp1.selection.models.simple',
                           'params': {
                               'list': self.invalid_article_name
                           },
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
                           'model': 'wp1.selection.models.simple',
                           'params': {
                               'list': self.valid_article_name
                           },
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
                           'model': 'wp1.selection.models.simple',
                           'params': {
                               'list': self.invalid_article_name
                           },
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
                           'model': 'wp1.selection.models.simple',
                           'params': {
                               'list': self.valid_article_name
                           },
                           'name': 'updated_list',
                           'project': 'my_project'
                       })
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
                           'model': 'wp1.selection.models.simple',
                           'params': {
                               'list': self.valid_article_name
                           },
                           'name': 'updated_list',
                           'project': 'my_project'
                       })
      self.assertEqual('404 NOT FOUND', rv.status)

  def test_empty_articles_create(self):
    self.app = create_app()
    with self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/',
                       json={
                           'model': 'wp1.selection.models.simple',
                           'params': {
                               'list': []
                           },
                           'name': 'my_list',
                           'project': 'my_project'
                       })
      self.assertEqual(self.empty_response, rv.get_json())

  def test_empty_name_create(self):
    self.app = create_app()
    with self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/',
                       json={
                           'model': 'wp1.selection.models.simple',
                           'params': {
                               'list': self.valid_article_name
                           },
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
                           'model': 'wp1.selection.models.simple',
                           'params': {
                               'list': self.valid_article_name
                           },
                           'name': 'my_list',
                           'project': ''
                       })
      self.assertEqual('400 BAD REQUEST', rv.status)

  def test_selection_unauthorized_user_create(self):
    self.app = create_app()
    with self.app.test_client() as client:
      rv = client.post('/v1/builders/',
                       json={
                           'model': 'wp1.selection.models.simple',
                           'articles': {
                               'list': self.valid_article_name
                           },
                           'name': 'my_list',
                           'project': 'my_project'
                       })
    self.assertEqual('401 UNAUTHORIZED', rv.status)

  def test_empty_articles_update(self):
    builder_id = self._insert_builder()
    self.app = create_app()
    with self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/%s' % builder_id,
                       json={
                           'model': 'wp1.selection.models.simple',
                           'params': {
                               'list': []
                           },
                           'name': 'my_list',
                           'project': 'my_project'
                       })
      self.assertEqual(self.empty_response, rv.get_json())

  def test_empty_list_update(self):
    builder_id = self._insert_builder()
    self.app = create_app()
    with self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/%s' % builder_id,
                       json={
                           'model': 'wp1.selection.models.simple',
                           'params': {
                               'list': self.valid_article_name
                           },
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
                           'model': 'wp1.selection.models.simple',
                           'params': {
                               'list': self.valid_article_name
                           },
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
                           'model': 'wp1.selection.models.simple',
                           'params': {
                               'list': self.valid_article_name
                           },
                           'name': 'my_list',
                           'project': 'my_project'
                       })
    self.assertEqual('401 UNAUTHORIZED', rv.status)

  def test_latest_selection(self):
    builder_id = self._insert_builder()
    self._insert_selections(builder_id)
    self.app = create_app()
    with self.app.test_client() as client:
      rv = client.get('/v1/builders/%s/selection/latest.tsv' % builder_id)
    self.assertEqual('302 FOUND', rv.status)
    self.assertEqual('http://credentials.not.found.fake/latest_object_key_tsv',
                     rv.headers['Location'])

  def test_latest_selection_bad_content_type(self):
    builder_id = self._insert_builder()
    self._insert_selections(builder_id)
    self.app = create_app()
    with self.app.test_client() as client:
      rv = client.get('/v1/builders/%s/selection/latest.foo' % builder_id)
    self.assertEqual('404 NOT FOUND', rv.status)

  def test_latest_selection_bad_builder_id(self):
    builder_id = self._insert_builder()
    self._insert_selections(builder_id)
    self.app = create_app()
    with self.app.test_client() as client:
      rv = client.get('/v1/builders/-1/selection/latest.tsv')
    self.assertEqual('404 NOT FOUND', rv.status)

  def test_latest_selection_no_selections(self):
    builder_id = self._insert_builder()
    self.app = create_app()
    with self.app.test_client() as client:
      rv = client.get('/v1/builders/%s/selection/latest.tsv' % builder_id)
    self.assertEqual('404 NOT FOUND', rv.status)

  @patch('wp1.logic.selection.connect_storage')
  def test_delete_successful(self, patched_connect_storage):
    builder_id = self._insert_builder()
    self._insert_selections(builder_id)
    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/%s/delete' % builder_id)
      self.assertEqual('200 OK', rv.status)
      self.assertEqual({'status': '204'}, rv.get_json())

  @patch('wp1.logic.selection.connect_storage')
  def test_delete_no_selections(self, patched_connect_storage):
    builder_id = self._insert_builder()

    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/%s/delete' % builder_id)
      self.assertEqual('200 OK', rv.status)
      self.assertEqual({'status': '204'}, rv.get_json())

  @patch('wp1.logic.selection.connect_storage')
  def test_delete_not_owner(self, patched_connect_storage):
    builder_id = self._insert_builder()
    self._insert_selections(builder_id)
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
      rv = client.post('/v1/builders/%s/delete' % builder_id)
      self.assertEqual('404 NOT FOUND', rv.status)

  @patch('wp1.logic.selection.connect_storage')
  def test_delete_no_builder(self, patched_connect_storage):
    builder_id = self._insert_builder()
    self._insert_selections(builder_id)

    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/-1/delete')
      self.assertEqual('404 NOT FOUND', rv.status)

  @patch('wp1.zimfarm.schedule_zim_file')
  def test_create_zim_file_for_builder(self, patched_schedule_zim_file):
    builder_id = self._insert_builder()
    self._insert_selections(builder_id)

    patched_schedule_zim_file.return_value = '1234-a'

    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/%s/zim' % builder_id,
                       json={'description': 'Test description'})
      self.assertEqual('204 NO CONTENT', rv.status)

    patched_schedule_zim_file.assert_called_once()
    with self.wp10db.cursor() as cursor:
      cursor.execute('SELECT z_task_id, z_status FROM zim_files '
                     'WHERE z_selection_id = 3')
      data = cursor.fetchone()

    self.assertEqual(b'1234-a', data['z_task_id'])
    self.assertEqual(b'REQUESTED', data['z_status'])

  @patch('wp1.zimfarm.schedule_zim_file')
  def test_create_zim_file_for_builder_not_found(self,
                                                 patched_schedule_zim_file):
    builder_id = self._insert_builder()
    self._insert_selections(builder_id)

    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/1234-not-found/zim',
                       json={'description': 'Test description'})
      self.assertEqual('404 NOT FOUND', rv.status)

  @patch('wp1.zimfarm.schedule_zim_file')
  def test_create_zim_file_for_builder_unauthorized(self,
                                                    patched_schedule_zim_file):
    builder_id = self._insert_builder()
    self._insert_selections(builder_id)

    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.UNAUTHORIZED_USER
      rv = client.post('/v1/builders/%s/zim' % builder_id,
                       json={'description': 'Test description'})
      self.assertEqual('403 FORBIDDEN', rv.status)

  @patch('wp1.zimfarm.schedule_zim_file')
  def test_create_zim_file_for_builder_500(self, patched_schedule_zim_file):
    builder_id = self._insert_builder()
    self._insert_selections(builder_id)

    patched_schedule_zim_file.side_effect = ZimFarmError

    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/%s/zim' % builder_id,
                       json={'description': 'Test description'})
      self.assertEqual('500 INTERNAL SERVER ERROR', rv.status)

  @patch('wp1.zimfarm.schedule_zim_file')
  def test_create_zim_file_for_builder_400(self, patched_schedule_zim_file):
    builder_id = self._insert_builder()
    self._insert_selections(builder_id)

    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/%s/zim' % builder_id, json={})
      self.assertEqual('400 BAD REQUEST', rv.status)

  @patch('wp1.web.builders.queues.poll_for_zim_file_status')
  def test_update_zimfarm_status(self, patched_poll):
    builder_id = self._insert_builder()
    self._insert_selections(builder_id)

    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/zim/status?token=hook-token-abc',
                       json={
                           '_id': 'task-id-1234',
                           'foo': 'bar'
                       })
      self.assertEqual('204 NO CONTENT', rv.status)
      patched_poll.assert_called_once()

    with self.wp10db.cursor() as cursor:
      cursor.execute('SELECT z_status, z_updated_at '
                     'FROM zim_files WHERE z_task_id = "task-id-1234"')
      status = cursor.fetchone()

    self.assertIsNotNone(status)
    self.assertEqual(b'ENDED', status['z_status'])
    self.assertIsNone(status['z_updated_at'])

  @patch('wp1.web.builders.queues.poll_for_zim_file_status')
  @patch('wp1.logic.selection.utcnow',
         return_value=datetime.datetime(2022, 12, 25, 0, 1, 2))
  def test_update_zimfarm_status_file_ready(self, patched_utcnow, patched_poll):
    builder_id = self._insert_builder()
    self._insert_selections(builder_id)

    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/zim/status?token=hook-token-abc',
                       json={
                           '_id': 'task-id-1234',
                           'foo': 'bar',
                           'files': {
                               'zimfile.1234': {
                                   'status': 'uploaded'
                               }
                           }
                       })
      self.assertEqual('204 NO CONTENT', rv.status)

    with self.wp10db.cursor() as cursor:
      cursor.execute('SELECT z_status, z_updated_at '
                     'FROM zim_files WHERE z_task_id = "task-id-1234"')
      status = cursor.fetchone()

    self.assertIsNotNone(status)
    self.assertEqual(b'FILE_READY', status['z_status'])
    self.assertEqual(b'20221225000102', status['z_updated_at'])

  def test_update_zimfarm_status_bad_token(self):
    builder_id = self._insert_builder()
    self._insert_selections(builder_id)

    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/zim/status?token=foo-bad-token',
                       json={
                           '_id': 'task-id-1234',
                           'foo': 'bar'
                       })
      self.assertEqual('403 FORBIDDEN', rv.status)

  def test_update_zimfarm_status_invalid_payload(self):
    builder_id = self._insert_builder()
    self._insert_selections(builder_id)

    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/zim/status?token=hook-token-abc',
                       json={
                           'baz': 'task-id-1234',
                           'foo': 'bar'
                       })
      self.assertEqual('400 BAD REQUEST', rv.status)

  @patch('wp1.web.builders.queues.poll_for_zim_file_status')
  def test_update_zimfarm_status_not_found_task_id(self, patched_poll):
    builder_id = self._insert_builder()
    self._insert_selections(builder_id)

    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/builders/zim/status?token=hook-token-abc',
                       json={
                           '_id': 'task-id-not-found',
                           'foo': 'bar'
                       })
      self.assertEqual('204 NO CONTENT', rv.status)

    patched_poll.assert_not_called()

  def test_zimfarm_status(self):
    builder_id = self._insert_builder()
    self._insert_selections(builder_id)
    with self.app.test_client() as client:
      rv = client.get('/v1/builders/%s/zim/status' % builder_id)
    self.assertEqual('200 OK', rv.status)
    self.assertEqual(
        {
            'error_url': 'https://fake.farm/v1/tasks/task-id-1234',
            'status': 'FILE_READY',
            'description': None,
            'long_description': None,
            'is_deleted': None,
        }, rv.get_json())

  @patch('wp1.logic.builder.zimfarm.zim_file_url_for_task_id',
         return_value='http://fake-file-host.fake/1234/file.zim')
  def test_latest_zim_file_for_builder(self, mock_zimfarm):
    builder_id = self._insert_builder()
    self._insert_selections(builder_id)
    self.app = create_app()
    with self.app.test_client() as client:
      rv = client.get('/v1/builders/%s/zim/latest' % builder_id)
    self.assertEqual('302 FOUND', rv.status)
    self.assertEqual('http://fake-file-host.fake/1234/file.zim',
                     rv.headers['Location'])

  def test_latest_zim_file_for_builder_404(self):
    builder_id = self._insert_builder()
    self._insert_selections(builder_id)
    self.app = create_app()
    with self.app.test_client() as client:
      rv = client.get('/v1/builders/abcd-1234/zim/latest')
    self.assertEqual('404 NOT FOUND', rv.status)
