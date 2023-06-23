import datetime
from unittest.mock import call, patch, MagicMock

import attr
import requests

from wp1.environment import Environment
from wp1.exceptions import ObjectNotFoundError, ZimFarmError
from wp1 import zimfarm
from wp1.base_db_test import BaseWpOneDbTest
from wp1.models.wp10.builder import Builder


class ZimFarmTest(BaseWpOneDbTest):

  def _insert_builder(self):
    value_dict = attr.asdict(self.builder)
    value_dict['b_current_version'] = 1
    value_dict['b_id'] = b'1a-2b-3c-4d'
    with self.wp10db.cursor() as cursor:
      cursor.execute(
          '''INSERT INTO builders
               (b_id, b_name, b_user_id, b_project, b_params, b_model, b_created_at,
                b_updated_at, b_current_version)
             VALUES
               (%(b_id)s, %(b_name)s, %(b_user_id)s, %(b_project)s, %(b_params)s,
                %(b_model)s, %(b_created_at)s, %(b_updated_at)s, %(b_current_version)s)
          ''', value_dict)
    self.wp10db.commit()
    return value_dict['b_id']

  def _insert_selection(self, id_):
    version = 1
    object_key = 'selections/foo/1234/name.tsv'
    content_type = 'text/tab-separated-values'
    builder_id = self.builder.b_id
    with self.wp10db.cursor() as cursor:
      cursor.execute(
          '''INSERT INTO selections
                (s_id, s_builder_id, s_updated_at, s_content_type, s_version, s_object_key)
              VALUES
                (%s, %s, '20191225044444', %s, %s, %s)''',
          (id_, builder_id, content_type, version, object_key))
    self.wp10db.commit()

  def setUp(self):
    super().setUp()
    self.builder = Builder(
        b_id=b'1a-2b-3c-4d',
        b_name=b'My Builder',
        b_user_id=1234,
        b_project=b'en.wikipedia.fake',
        b_model=b'wp1.selection.models.simple',
        b_params=b'{"list": ["a", "b", "c"]}',
        b_created_at=b'20191225044444',
        b_updated_at=b'20191225044444',
        b_current_version=1,
    )

    self.builder_2 = Builder(
        b_id=b'1a-2b-3c-4d',
        b_name=b'My Builder',
        b_user_id=1234,
        b_project=b'en.wikipedia.fake',
        b_model=b'wp1.selection.models.simple',
        b_params=b'{"list": ["a", "b", "c"]}',
    )

  def test_get_params(self):
    s3 = MagicMock()
    s3.client.head_object.return_value = {'ContentLength': 20000000}
    self._insert_builder()
    self._insert_selection(b'abc-12345-def')

    actual = zimfarm._get_params(
        s3,
        self.wp10db,
        self.builder,
        description='This is the short description',
        long_description='This is the long description')

    self.maxDiff = None
    self.assertEqual(
        {
            'name': 'wp1_selection_def',
            'language': {
                'code': 'eng',
                'name_en': 'English',
                'name_native': 'English'
            },
            'category': 'wikipedia',
            'periodicity': 'manually',
            'tags': [],
            'enabled': True,
            'notification': {
                'ended': {
                    'webhook': [
                        'http://test.server.fake/v1/builders/zim/status?token=hook-token-abc'
                    ],
                },
            },
            'config': {
                'task_name': 'mwoffliner',
                'warehouse_path': '/wikipedia',
                'image': {
                    'name': 'ghcr.io/openzim/mwoffliner',
                    'tag': 'latest'
                },
                'resources': {
                    'cpu': 3,
                    'memory': 6442450944,
                    'disk': 42949672960,
                },
                'platform': 'wikimedia',
                'monitor': False,
                'flags': {
                    'customZimDescription':
                        'This is the short description',
                    'customZimLongDescription':
                        'This is the long description',
                    'mwUrl':
                        'https://en.wikipedia.fake/',
                    'adminEmail':
                        'contact+wp1@kiwix.org',
                    'articleList':
                        'http://credentials.not.found.fake/selections/foo/1234/name.tsv',
                    'customZimTitle':
                        'My Builder',
                    'filenamePrefix':
                        'MyBuilder-def'
                }
            }
        }, actual)

  def test_get_params_missing_builder(self):
    s3 = MagicMock()
    self._insert_builder()
    self._insert_selection(b'abc-12345-def')

    with self.assertRaises(ObjectNotFoundError):
      zimfarm._get_params(s3, self.wp10db, None)

  @patch('wp1.zimfarm.requests')
  def test_request_zimfarm_token(self, mock_requests):
    redis = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {'access_token': 'abcdef'}
    mock_requests.post.return_value = mock_response

    actual = zimfarm.request_zimfarm_token(redis)

    self.assertEqual('abcdef', actual)

  @patch('wp1.zimfarm.requests')
  def test_request_zimfarm_token_posts_with_correct_data(self, mock_requests):
    redis = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {'access_token': 'abcdef'}
    mock_requests.post.return_value = mock_response

    actual = zimfarm.request_zimfarm_token(redis)

    mock_requests.post.assert_called_once_with(
        'https://fake.farm/v1/auth/authorize',
        headers={
            'User-Agent': 'WP 1.0 bot 1.0.0/Audiodude <audiodude@gmail.com>'
        },
        data={
            'username': 'farmuser',
            'password': 'farmpass'
        })

  @patch('wp1.zimfarm.requests')
  def test_request_zimfarm_token_raises_for_status(self, mock_requests):
    redis = MagicMock()
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
    mock_requests.exceptions.HTTPError = requests.exceptions.HTTPError
    mock_requests.post.return_value = mock_response

    with self.assertRaises(ZimFarmError):
      actual = zimfarm.request_zimfarm_token(redis)

  @patch('wp1.zimfarm.CREDENTIALS', {Environment.TEST: {}})
  def test_request_zimfarm_token_no_creds(self):
    redis = MagicMock()

    with self.assertRaises(ZimFarmError):
      zimfarm.request_zimfarm_token(redis)

  @patch('wp1.zimfarm.requests')
  def test_refresh_zimfarm_token(self, mock_requests):
    redis = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {'access_token': 'abcdef'}
    mock_requests.post.return_value = mock_response

    refresh_token = '12345'
    actual = zimfarm.refresh_zimfarm_token(redis, refresh_token)

    self.assertEqual('abcdef', actual)

  @patch('wp1.zimfarm.requests')
  def test_refresh_zimfarm_token_posts_with_correct_data(self, mock_requests):
    redis = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {'access_token': 'abcdef'}
    mock_requests.post.return_value = mock_response

    refresh_token = '12345'
    actual = zimfarm.refresh_zimfarm_token(redis, refresh_token)

    mock_requests.post.assert_called_once_with(
        'https://fake.farm/v1/auth/token',
        headers={
            'User-Agent': 'WP 1.0 bot 1.0.0/Audiodude <audiodude@gmail.com>',
            'refresh-token': '12345'
        })

  @patch('wp1.zimfarm.requests')
  def test_refresh_zimfarm_token_raises_for_status(self, mock_requests):
    redis = MagicMock()
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
    mock_requests.exceptions.HTTPError = requests.exceptions.HTTPError
    mock_requests.post.return_value = mock_response

    with self.assertRaises(ZimFarmError):
      actual = zimfarm.refresh_zimfarm_token(redis, '12345')

  @patch('wp1.zimfarm.CREDENTIALS', {Environment.TEST: {}})
  def test_refresh_zimfarm_token_no_creds(self):
    redis = MagicMock()

    with self.assertRaises(ZimFarmError):
      zimfarm.refresh_zimfarm_token(redis, '12345')

  @patch('wp1.zimfarm.request_zimfarm_token')
  def test_get_zimfarm_token_no_data(self, request_token_mock):
    redis = MagicMock()
    redis.hgetall.return_value = None

    request_token_mock.return_value = 'bcdefg'
    actual = zimfarm.get_zimfarm_token(redis)
    self.assertEqual(actual, 'bcdefg')

  @patch('wp1.zimfarm.request_zimfarm_token')
  def test_get_zimfarm_token_no_refresh_token(self, request_token_mock):
    redis = MagicMock()
    redis.hgetall.return_value = {
        'expires_in': '2023-01-01T00:00:01Z',
        'access_token': 'abcdef',
    }

    request_token_mock.return_value = 'bcdefg'
    actual = zimfarm.get_zimfarm_token(redis)
    self.assertEqual(actual, 'bcdefg')

  @patch('wp1.zimfarm.get_current_datetime')
  def test_get_zimfarm_token_access_token_not_expired(self,
                                                      current_datetime_mock):
    current_datetime_mock.return_value = datetime.datetime(
        2022, 12, 25, 5, 5, 55)

    redis = MagicMock()
    redis.hgetall.return_value = {
        'expires_in': '2023-01-01T00:00:01Z',
        'refresh_token': '12345',
        'access_token': 'abcdef',
    }

    actual = zimfarm.get_zimfarm_token(redis)

    self.assertEqual(actual, 'abcdef')

  @patch('wp1.zimfarm.get_current_datetime')
  @patch('wp1.zimfarm.refresh_zimfarm_token')
  def test_get_zimfarm_token_access_token_expired(self, refresh_token_mock,
                                                  current_datetime_mock):
    current_datetime_mock.return_value = datetime.datetime(
        2022, 12, 25, 5, 5, 55)
    refresh_token_mock.return_value = 'bcdefg'

    redis = MagicMock()
    redis.hgetall.return_value = {
        'expires_in': '2022-12-01T00:00:01Z',
        'refresh_token': '12345',
        'access_token': 'abcdef',
    }

    actual = zimfarm.get_zimfarm_token(redis)

    self.assertEqual(actual, 'bcdefg')

  @patch('wp1.zimfarm.requests')
  @patch('wp1.zimfarm.get_zimfarm_token')
  @patch('wp1.zimfarm._get_params')
  def test_schedule_zim_file(self, get_params_mock, get_token_mock,
                             mock_requests):
    redis = MagicMock()
    s3 = MagicMock()
    get_params_mock.return_value = {'name': 'bar'}
    get_token_mock.return_value = 'abcdef'
    mock_response = MagicMock()
    mock_response.json.return_value = {'requested': ['9876']}
    mock_requests.post.side_effect = (MagicMock(), mock_response, MagicMock())

    actual = zimfarm.schedule_zim_file(s3, redis, self.wp10db, self.builder)

    self.assertEqual('9876', actual)

  @patch('wp1.zimfarm.requests')
  @patch('wp1.zimfarm.get_zimfarm_token')
  def test_schedule_zim_file_missing_builder(self, get_token_mock,
                                             mock_requests):
    self._insert_builder()
    self._insert_selection(b'abc-12345-def')

    redis = MagicMock()
    s3 = MagicMock()
    get_token_mock.return_value = 'abcdef'
    mock_response = MagicMock()
    mock_response.json.return_value = {'requested': ['9876']}
    mock_requests.post.side_effect = (MagicMock(), mock_response, MagicMock())

    with self.assertRaises(ObjectNotFoundError):
      actual = zimfarm.schedule_zim_file(s3, redis, self.wp10db, None)

  @patch('wp1.zimfarm.requests')
  @patch('wp1.zimfarm.get_zimfarm_token')
  @patch('wp1.zimfarm._get_params')
  def test_schedule_zim_file_post_requests(self, get_params_mock,
                                           get_token_mock, mock_requests):
    redis = MagicMock()
    s3 = MagicMock()
    get_params_mock.return_value = {'name': 'bar'}
    get_token_mock.return_value = 'abcdef'
    mock_response = MagicMock()
    mock_response.json.return_value = {'requested': ['9876']}
    mock_requests.post.side_effect = (MagicMock(), mock_response)

    actual = zimfarm.schedule_zim_file(s3, redis, self.wp10db, self.builder)

    schedule_create_call = call(
        'https://fake.farm/v1/schedules/',
        headers={
            'Authorization': 'Token abcdef',
            'User-Agent': 'WP 1.0 bot 1.0.0/Audiodude <audiodude@gmail.com>'
        },
        json={'name': 'bar'})
    task_request_call = call(
        'https://fake.farm/v1/requested-tasks/',
        headers={
            'Authorization': 'Token abcdef',
            'User-Agent': 'WP 1.0 bot 1.0.0/Audiodude <audiodude@gmail.com>'
        },
        json={'schedule_names': ['bar']})

    mock_requests.post.assert_has_calls(
        (schedule_create_call, task_request_call))
    mock_requests.delete.assert_called_once_with(
        'https://fake.farm/v1/schedules/bar',
        headers={
            'Authorization': 'Token abcdef',
            'User-Agent': 'WP 1.0 bot 1.0.0/Audiodude <audiodude@gmail.com>'
        },
    )

  @patch('wp1.zimfarm.requests')
  @patch('wp1.zimfarm.get_zimfarm_token')
  @patch('wp1.zimfarm._get_params')
  def test_schedule_zim_file_schedule_create_raises(self, get_params_mock,
                                                    get_token_mock,
                                                    mock_requests):
    redis = MagicMock()
    s3 = MagicMock()
    get_params_mock.return_value = {'name': 'bar'}
    get_token_mock.return_value = 'abcdef'
    mock_response = MagicMock()
    mock_response.json.return_value = {'requested': ['9876']}
    create_schedule_response = MagicMock()
    create_schedule_response.raise_for_status.side_effect = requests.exceptions.HTTPError
    mock_requests.exceptions.HTTPError = requests.exceptions.HTTPError
    mock_requests.post.side_effect = (create_schedule_response, mock_response)

    with self.assertRaises(ZimFarmError):
      actual = zimfarm.schedule_zim_file(s3, redis, self.wp10db, self.builder)

  @patch('wp1.zimfarm.requests')
  @patch('wp1.zimfarm.get_zimfarm_token')
  @patch('wp1.zimfarm._get_params')
  def test_schedule_zim_file_task_create_raises(self, get_params_mock,
                                                get_token_mock, mock_requests):
    redis = MagicMock()
    s3 = MagicMock()
    get_params_mock.return_value = {'name': 'bar'}
    get_token_mock.return_value = 'abcdef'
    mock_response = MagicMock()
    mock_response.json.side_effect = requests.exceptions.HTTPError
    mock_requests.exceptions.HTTPError = requests.exceptions.HTTPError
    mock_requests.post.side_effect = (
        MagicMock(),
        mock_response,
    )

    with self.assertRaises(ZimFarmError):
      actual = zimfarm.schedule_zim_file(s3, redis, self.wp10db, self.builder)

  @patch('wp1.zimfarm.requests')
  @patch('wp1.zimfarm.get_zimfarm_token')
  @patch('wp1.zimfarm._get_params')
  def test_schedule_zim_file_delete_schedule_even_if_task_create_raises(
      self, get_params_mock, get_token_mock, mock_requests):
    redis = MagicMock()
    s3 = MagicMock()
    get_params_mock.return_value = {'name': 'bar'}
    get_token_mock.return_value = 'abcdef'
    mock_response = MagicMock()
    mock_response.json.side_effect = requests.exceptions.HTTPError
    mock_requests.post.side_effect = (
        MagicMock(),
        mock_response,
    )
    mock_requests.exceptions.HTTPError = requests.exceptions.HTTPError

    with self.assertRaises(ZimFarmError):
      actual = zimfarm.schedule_zim_file(s3, redis, self.wp10db, self.builder)

    mock_requests.delete.assert_called_once()

  @patch('wp1.zimfarm.requests')
  @patch('wp1.zimfarm.get_zimfarm_token')
  @patch('wp1.zimfarm._get_params')
  def test_schedule_zim_file_missing_task_id(self, get_params_mock,
                                             get_token_mock, mock_requests):
    redis = MagicMock()
    s3 = MagicMock()
    get_params_mock.return_value = {'name': 'bar'}
    get_token_mock.return_value = 'abcdef'
    mock_response = MagicMock()
    mock_response.json.return_value = {'requested': []}
    mock_requests.exceptions.HTTPError = requests.exceptions.HTTPError
    mock_requests.post.side_effect = (MagicMock(), mock_response, MagicMock())

    with self.assertRaises(ZimFarmError):
      actual = zimfarm.schedule_zim_file(s3, redis, self.wp10db, self.builder)

  @patch('wp1.zimfarm.requests.get')
  def test_is_zim_file_ready(self, patched_get):
    resp = MagicMock()
    resp.json.return_value = {'files': {'foo.zim': {'status': 'uploaded'}}}
    patched_get.return_value = resp
    actual = zimfarm.is_zim_file_ready('foo-bar')
    self.assertEqual('FILE_READY', actual)

  @patch('wp1.zimfarm.requests.get')
  def test_is_zim_file_ready_requested(self, patched_get):
    resp = MagicMock()
    resp.json.return_value = {'files': {'foo.zim': {'status': 'success'}}}
    patched_get.return_value = resp
    actual = zimfarm.is_zim_file_ready('foo-bar')
    self.assertEqual('REQUESTED', actual)

  @patch('wp1.zimfarm.requests.get')
  def test_is_zim_file_ready_failed(self, patched_get):
    resp = MagicMock()
    resp.json.return_value = {
        'status': 'failed',
        'files': {
            'foo.zim': {
                'status': 'failed'
            }
        }
    }
    patched_get.return_value = resp
    actual = zimfarm.is_zim_file_ready('foo-bar')
    self.assertEqual('FAILED', actual)

  @patch('wp1.zimfarm.requests.get')
  def test_is_zim_file_ready_non_200(self, patched_get):
    resp = MagicMock()
    resp.raise_for_status.side_effect = requests.exceptions.HTTPError
    patched_get.return_value = resp
    actual = zimfarm.is_zim_file_ready('foo-bar')
    self.assertEqual('REQUESTED', actual)

  @patch('wp1.zimfarm.requests.get')
  def test_zim_file_url_for_task_id(self, patched_get):
    resp = MagicMock()
    resp.json.return_value = {
        'config': {
            'warehouse_path': '/wikipedia'
        },
        'files': {
            'foo.zim': {
                'name': 'foo.zim'
            }
        }
    }
    patched_get.return_value = resp
    actual = zimfarm.zim_file_url_for_task_id('foo-bar')
    self.assertEqual(
        'https://fake.wasabisys.com/org-kiwix-zimit/wikipedia/foo.zim', actual)

  @patch('wp1.zimfarm.requests.get')
  def test_zim_file_url_for_task_id_non_200(self, patched_get):
    resp = MagicMock()
    resp.raise_for_status.side_effect = requests.exceptions.HTTPError
    patched_get.return_value = resp
    actual = zimfarm.zim_file_url_for_task_id('foo-bar')
    self.assertIsNone(actual)

  @patch('wp1.zimfarm.requests.get')
  def test_zim_file_url_for_task_id_missing_name(self, patched_get):
    resp = MagicMock()
    resp.json.return_value = {
        'config': {
            'warehouse_path': '/wikipedia'
        },
        'files': {
            'foo.zim': {}
        }
    }
    patched_get.return_value = resp
    with self.assertRaises(ZimFarmError):
      actual = zimfarm.zim_file_url_for_task_id('foo-bar')

  @patch('wp1.zimfarm.requests.get')
  def test_zim_file_url_for_task_id_missing_warehouse_path(self, patched_get):
    resp = MagicMock()
    resp.json.return_value = {
        'config': {},
        'files': {
            'foo.zim': {
                'name': 'foo.zim'
            }
        }
    }
    patched_get.return_value = resp
    with self.assertRaises(ZimFarmError):
      actual = zimfarm.zim_file_url_for_task_id('foo-bar')

  @patch('wp1.zimfarm.requests.get')
  @patch('wp1.zimfarm.CREDENTIALS', {Environment.TEST: {}})
  def test_zim_file_url_for_task_id_missing_s3_url(self, patched_get):
    resp = MagicMock()
    resp.json.return_value = {
        'config': {
            'warehouse_path': '/wikipedia'
        },
        'files': {
            'foo.zim': {
                'name': 'foo.zim'
            }
        }
    }
    patched_get.return_value = resp
    with self.assertRaises(ZimFarmError):
      actual = zimfarm.zim_file_url_for_task_id('foo-bar')

  @patch('wp1.zimfarm.get_zimfarm_token')
  @patch('wp1.zimfarm.requests.delete')
  def test_cancel_zim_by_task_id(self, patched_delete,
                                 patched_get_zimfarm_token):
    patched_get_zimfarm_token.return_value = 'foo-token'
    redis = MagicMock()

    zimfarm.cancel_zim_by_task_id(redis, 'task-abc-123')
    patched_delete.assert_called_once_with(
        'https://fake.farm/v1/requested-tasks/task-abc-123',
        headers={
            'Authorization': 'Token foo-token',
            'User-Agent': 'WP 1.0 bot 1.0.0/Audiodude <audiodude@gmail.com>'
        })

  @patch('wp1.zimfarm.get_zimfarm_token')
  @patch('wp1.zimfarm.requests.delete')
  @patch('wp1.zimfarm.requests.post')
  def test_cancel_zim_by_task_id_first_delete_404(self, patched_post,
                                                  patched_delete,
                                                  patched_get_zimfarm_token):
    patched_get_zimfarm_token.return_value = 'foo-token'
    redis = MagicMock()
    response_404 = MagicMock()
    response_404.status_code = 404
    response_404.raise_for_status.side_effect = requests.exceptions.HTTPError
    patched_delete.return_value = response_404

    zimfarm.cancel_zim_by_task_id(redis, 'task-abc-123')
    patched_delete.assert_any_call(
        'https://fake.farm/v1/requested-tasks/task-abc-123',
        headers={
            'Authorization': 'Token foo-token',
            'User-Agent': 'WP 1.0 bot 1.0.0/Audiodude <audiodude@gmail.com>'
        })
    patched_post.assert_any_call(
        'https://fake.farm/v1/tasks/task-abc-123/cancel',
        headers={
            'Authorization': 'Token foo-token',
            'User-Agent': 'WP 1.0 bot 1.0.0/Audiodude <audiodude@gmail.com>'
        })

  @patch('wp1.zimfarm.get_zimfarm_token')
  @patch('wp1.zimfarm.requests.delete')
  @patch('wp1.zimfarm.requests.post')
  def test_cancel_zim_by_task_id_first_delete_other_error(
      self, patched_post, patched_delete, patched_get_zimfarm_token):
    patched_get_zimfarm_token.return_value = 'foo-token'
    redis = MagicMock()
    response_500 = MagicMock()
    response_500.status_code = 500
    response_500.raise_for_status.side_effect = requests.exceptions.HTTPError
    patched_delete.return_value = response_500

    with self.assertRaises(ZimFarmError):
      zimfarm.cancel_zim_by_task_id(redis, 'task-abc-123')

  @patch('wp1.zimfarm.get_zimfarm_token')
  @patch('wp1.zimfarm.requests.delete')
  @patch('wp1.zimfarm.requests.post')
  def test_cancel_zim_by_task_id_second_delete_error(self, patched_post,
                                                     patched_delete,
                                                     patched_get_zimfarm_token):
    patched_get_zimfarm_token.return_value = 'foo-token'
    redis = MagicMock()
    response_404 = MagicMock()
    response_404.status_code = 404
    response_404.raise_for_status.side_effect = requests.exceptions.HTTPError
    patched_delete.return_value = response_404
    second_response = MagicMock()
    second_response.status_code = 404
    second_response.raise_for_status.side_effect = requests.exceptions.HTTPError
    patched_post.return_value = second_response

    with self.assertRaises(ZimFarmError):
      zimfarm.cancel_zim_by_task_id(redis, 'task-abc-123')
