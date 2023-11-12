import datetime
from unittest.mock import call, patch, MagicMock, ANY

import attr

from wp1.base_db_test import BaseWpOneDbTest
from wp1.exceptions import ObjectNotFoundError, UserNotAuthorizedError, ZimFarmError
from wp1.logic import builder as logic_builder
from wp1.models.wp10.builder import Builder


class BuilderTest(BaseWpOneDbTest):

  expected_builder = {
      'b_id': b'1a-2b-3c-4d',
      'b_name': b'My Builder',
      'b_user_id': 1234,
      'b_project': b'en.wikipedia.fake',
      'b_model': b'wp1.selection.models.simple',
      'b_params': b'{"list": ["a", "b", "c"]}',
      'b_created_at': b'20191225044444',
      'b_updated_at': b'20191225044444',
      'b_current_version': 0,
      'b_selection_zim_version': 0,
  }

  expected_lists = [{
      'id':
          '1a-2b-3c-4d',
      'name':
          'My Builder',
      'project':
          'en.wikipedia.fake',
      'created_at':
          1577249084,
      'updated_at':
          1577249084,
      'model':
          'wp1.selection.models.simple',
      's_id':
          '1',
      's_updated_at':
          1577249084,
      's_content_type':
          'text/tab-separated-values',
      's_extension':
          'tsv',
      's_url':
          'http://test.server.fake/v1/builders/1a-2b-3c-4d/selection/latest.tsv',
      's_status':
          'OK',
      'z_updated_at':
          None,
      'z_url':
          None,
      'z_status':
          'NOT_REQUESTED',
      'z_is_deleted':
          None,
  }]

  expected_lists_with_multiple_selections = [
      {
          'id':
              '1a-2b-3c-4d',
          'name':
              'My Builder',
          'project':
              'en.wikipedia.fake',
          'created_at':
              1577249084,
          'updated_at':
              1577249084,
          'model':
              'wp1.selection.models.simple',
          's_id':
              '2',
          's_updated_at':
              1577249084,
          's_content_type':
              'application/vnd.ms-excel',
          's_extension':
              'xls',
          's_url':
              'http://test.server.fake/v1/builders/1a-2b-3c-4d/selection/latest.xls',
          's_status':
              'OK',
          'z_updated_at':
              None,
          'z_url':
              None,
          'z_status':
              'NOT_REQUESTED',
          'z_is_deleted':
              None,
      },
      {
          'id':
              '1a-2b-3c-4d',
          'name':
              'My Builder',
          'project':
              'en.wikipedia.fake',
          'created_at':
              1577249084,
          'updated_at':
              1577249084,
          'model':
              'wp1.selection.models.simple',
          's_id':
              '1',
          's_updated_at':
              1577249084,
          's_content_type':
              'text/tab-separated-values',
          's_extension':
              'tsv',
          's_url':
              'http://test.server.fake/v1/builders/1a-2b-3c-4d/selection/latest.tsv',
          's_status':
              'OK',
          'z_updated_at':
              None,
          'z_url':
              None,
          'z_status':
              'NOT_REQUESTED',
          'z_is_deleted':
              None,
      },
  ]

  expected_lists_with_no_selections = [{
      'id': '1a-2b-3c-4d',
      'name': 'My Builder',
      'project': 'en.wikipedia.fake',
      'created_at': 1577249084,
      'updated_at': 1577249084,
      'model': 'wp1.selection.models.simple',
      's_id': None,
      's_updated_at': None,
      's_content_type': None,
      's_extension': None,
      's_url': None,
      's_status': None,
      'z_updated_at': None,
      'z_url': None,
      'z_status': None,
      'z_is_deleted': None,
  }]

  expected_lists_with_unmapped_selections = [{
      'id': '1a-2b-3c-4d',
      'name': 'My Builder',
      'project': 'en.wikipedia.fake',
      'created_at': 1577249084,
      'updated_at': 1577249084,
      'model': 'wp1.selection.models.simple',
      's_id': '1',
      's_updated_at': 1577249084,
      's_content_type': 'foo/bar-baz',
      's_extension': '???',
      's_url': None,
      's_status': 'OK',
      'z_updated_at': None,
      'z_url': None,
      'z_status': 'NOT_REQUESTED',
      'z_is_deleted': None,
  }]

  expected_list_with_zimfarm_status = [{
      'id':
          '1a-2b-3c-4d',
      'name':
          'My Builder',
      'project':
          'en.wikipedia.fake',
      'created_at':
          1577249084,
      'updated_at':
          1577249084,
      'model':
          'wp1.selection.models.simple',
      's_id':
          '1',
      's_updated_at':
          1577249084,
      's_content_type':
          'text/tab-separated-values',
      's_extension':
          'tsv',
      's_url':
          'http://test.server.fake/v1/builders/1a-2b-3c-4d/selection/latest.tsv',
      's_status':
          'OK',
      'z_updated_at':
          1671927082,
      'z_url':
          'http://test.server.fake/v1/builders/1a-2b-3c-4d/zim/latest',
      'z_status':
          'FILE_READY',
      'z_is_deleted':
          True,
  }]

  def _insert_builder(self, current_version=None, zim_version=None):
    if current_version is None:
      current_version = 1
    value_dict = attr.asdict(self.builder)
    value_dict['b_current_version'] = current_version
    value_dict['b_id'] = b'1a-2b-3c-4d'
    if zim_version is not None:
      value_dict['b_selection_zim_version'] = zim_version
    with self.wp10db.cursor() as cursor:
      cursor.execute(
          '''INSERT INTO builders
               (b_id, b_name, b_user_id, b_project, b_params, b_model, b_created_at,
                b_updated_at, b_current_version, b_selection_zim_version)
             VALUES
               (%(b_id)s, %(b_name)s, %(b_user_id)s, %(b_project)s, %(b_params)s,
                %(b_model)s, %(b_created_at)s, %(b_updated_at)s, %(b_current_version)s,
                %(b_selection_zim_version)s)
          ''', value_dict)
    self.wp10db.commit()
    return value_dict['b_id']

  def _insert_selection(self,
                        id_,
                        content_type,
                        version=1,
                        object_key='selections/foo/1234/name.tsv',
                        builder_id=b'1a-2b-3c-4d',
                        has_errors=False,
                        zim_file_ready=False,
                        zim_task_id='5678',
                        skip_zim=False):
    if has_errors:
      status = 'CAN_RETRY'
      error_messages = '{"error_messages":["There was an error"]}'
    else:
      status = 'OK'
      error_messages = None

    zimfarm_status = b'NOT_REQUESTED'
    zim_file_updated_at = None
    if zim_file_ready:
      zimfarm_status = b'FILE_READY'
      zim_file_updated_at = b'20221225001122'

    with self.wp10db.cursor() as cursor:
      cursor.execute(
          '''INSERT INTO selections
               (s_id, s_builder_id, s_content_type, s_updated_at, s_version,
                s_object_key, s_status, s_error_messages)
             VALUES
               (%s, %s, %s, "20191225044444", %s, %s, %s, %s)
          ''', (id_, builder_id, content_type, version, object_key, status,
                error_messages))
      if not skip_zim:
        cursor.execute(
            '''INSERT INTO zim_files
                 (z_selection_id, z_task_id, z_status, z_updated_at,
                  z_requested_at)
               VALUES
                 (%s, %s, %s, %s, "20230101020202")
            ''', (id_, zim_task_id, zimfarm_status, zim_file_updated_at))
    self.wp10db.commit()

  def _get_builder_by_user_id(self):
    with self.wp10db.cursor() as cursor:
      cursor.execute('SELECT * FROM builders WHERE b_user_id=%(b_user_id)s',
                     {'b_user_id': '1234'})
      db_lists = cursor.fetchone()
      return db_lists

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
        b_selection_zim_version=1,
    )

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  @patch('wp1.models.wp10.builder.builder_id', return_value=b'1a-2b-3c-4d')
  def test_create_or_update_builder_create(self, mock_builder_id, mock_utcnow):
    logic_builder.create_or_update_builder(self.wp10db, 'My Builder', '1234',
                                           'en.wikipedia.fake',
                                           {'list': ['a', 'b', 'c']},
                                           'wp1.selection.models.simple')
    actual = self._get_builder_by_user_id()
    self.assertEqual(self.expected_builder, actual)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2020, 1, 1, 5, 55, 55))
  def test_create_or_update_builder_update(self, mock_utcnow):
    id_ = self._insert_builder()
    actual = logic_builder.create_or_update_builder(
        self.wp10db,
        'Builder 2',
        '1234',
        'zz.wikipedia.fake', {'list': ['a', 'b', 'c', 'd']},
        'wp1.selection.models.simple',
        builder_id=id_)
    self.assertTrue(actual)
    expected = dict(**self.expected_builder)
    expected['b_name'] = b'Builder 2'
    expected['b_project'] = b'zz.wikipedia.fake'
    expected['b_params'] = b'{"list": ["a", "b", "c", "d"]}'
    expected['b_updated_at'] = b'20200101055555'
    expected['b_current_version'] = 1
    expected['b_selection_zim_version'] = 1
    actual = self._get_builder_by_user_id()
    self.assertEqual(expected, actual)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  @patch('wp1.models.wp10.builder.builder_id', return_value=b'1a-2b-3c-4d')
  def test_insert_builder(self, mock_builder_id, mock_utcnow):
    logic_builder.insert_builder(self.wp10db, self.builder)
    actual = self._get_builder_by_user_id()
    self.assertEqual(self.expected_builder, actual)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  @patch('wp1.models.wp10.builder.builder_id', return_value=b'1a-2b-3c-4d')
  def test_insert_builder_returns_id(self, mock_builder_id, mock_utcnow):
    actual = logic_builder.insert_builder(self.wp10db, self.builder)
    self.assertEqual(b'1a-2b-3c-4d', actual)

  def test_get_builder(self):
    id_ = self._insert_builder()
    actual = logic_builder.get_builder(self.wp10db, id_)
    self.builder.b_id = id_
    self.assertEqual(self.builder, actual)

  @patch('wp1.logic.builder.wp10_connect')
  @patch('wp1.logic.builder.connect_storage')
  def test_materialize_builder(self, patched_connect_storage,
                               patched_connect_wp10):
    patched_connect_wp10.return_value = self.wp10db
    TestBuilderClass = MagicMock()
    materialize_mock = MagicMock()
    TestBuilderClass.return_value = materialize_mock

    orig_close = self.wp10db.close
    try:
      self.wp10db.close = lambda: True
      id_ = self._insert_builder()
      self._insert_selection(1, 'text/tab-separated-values')

      logic_builder.materialize_builder(TestBuilderClass, id_,
                                        'text/tab-separated-values')
      materialize_mock.materialize.assert_called_once_with(
          ANY, ANY, self.builder, 'text/tab-separated-values', 2)
    finally:
      self.wp10db.close = orig_close

    builder = self._get_builder_by_user_id()
    expected = dict(**self.expected_builder)
    expected['b_current_version'] = 2
    expected['b_selection_zim_version'] = 2
    self.assertEqual(expected, builder)

  @patch('wp1.logic.builder.wp10_connect')
  @patch('wp1.logic.builder.redis_connect')
  @patch('wp1.logic.builder.connect_storage')
  @patch('wp1.logic.builder.schedule_zim_file')
  def test_materialize_builder_no_update_zim_version(self,
                                                     patched_schedule_zim_file,
                                                     patched_connect_storage,
                                                     patched_redis_connect,
                                                     patched_connect_wp10):
    s3 = MagicMock()
    redis = MagicMock()
    patched_connect_wp10.return_value = self.wp10db
    patched_connect_storage.return_value = s3
    patched_redis_connect.return_value = redis
    TestBuilderClass = MagicMock()
    materialize_mock = MagicMock()
    TestBuilderClass.return_value = materialize_mock

    orig_close = self.wp10db.close
    try:
      self.wp10db.close = lambda: True
      id_ = self._insert_builder()
      self._insert_selection(1,
                             'text/tab-separated-values',
                             zim_file_ready=True)

      logic_builder.materialize_builder(TestBuilderClass, id_,
                                        'text/tab-separated-values')
      patched_schedule_zim_file.assert_called_once_with(s3,
                                                        redis,
                                                        self.wp10db,
                                                        id_,
                                                        description=None,
                                                        long_description=None)
    finally:
      self.wp10db.close = orig_close

    builder = self._get_builder_by_user_id()
    expected = dict(**self.expected_builder)
    expected['b_current_version'] = 2
    expected['b_selection_zim_version'] = 1
    self.assertEqual(expected, builder)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_get_builders(self, mock_utcnow):
    self._insert_selection(1, 'text/tab-separated-values')
    self._insert_builder()
    article_data = logic_builder.get_builders_with_selections(self.wp10db, 1234)
    self.assertEqual(self.expected_lists, article_data)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_get_builders_with_multiple_selections(self, mock_utcnow):
    self._insert_selection(1,
                           'text/tab-separated-values',
                           object_key='object_key_1')
    self._insert_selection(2,
                           'application/vnd.ms-excel',
                           object_key='object_key_2')
    self._insert_builder()
    article_data = logic_builder.get_builders_with_selections(self.wp10db, 1234)
    self.assertObjectListsEqual(self.expected_lists_with_multiple_selections,
                                article_data)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_get_builders_with_no_selections(self, mock_utcnow):
    self._insert_builder()
    article_data = logic_builder.get_builders_with_selections(self.wp10db, 1234)
    self.assertEqual(self.expected_lists_with_no_selections, article_data)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_get_builders_with_selections_no_zim_files(self, mock_utcnow):
    id_ = self._insert_builder()
    self._insert_selection(1, 'text/tab-separated-values', skip_zim=True)
    article_data = logic_builder.get_builders_with_selections(self.wp10db, 1234)
    self.assertEqual(self.expected_lists, article_data)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_get_builders_empty_lists(self, mock_utcnow):
    self._insert_selection(1, 'text/tab-separated-values')
    id_ = self._insert_builder()
    article_data = logic_builder.get_builders_with_selections(
        self.wp10db, '0000')
    self.assertEqual([], article_data)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def teest_get_builders_ignores_old_versions(self, mock_utcnow):
    self._insert_selection(1, 'text/tab-separated-values', 1)
    self._insert_selection(2, 'application/vnd.ms-excel', 1)
    self._insert_selection(3, 'text/tab-separated-values', 2)
    self._insert_selection(4, 'application/vnd.ms-excel', 2)
    id_ = self._insert_builder()
    article_data = logic_builder.get_builders_with_selections(self.wp10db, id_)
    self.assertObjectListsEqual(self.expected_lists_with_multiple_selections,
                                article_data)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_get_builders_with_selection_no_builders(self, mock_utcnow):
    self._insert_selection(1, 'text/tab-separated-values')
    article_data = logic_builder.get_builders_with_selections(
        self.wp10db, '0000')
    self.assertEqual([], article_data)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_get_builders_with_unmapped_content_type(self, mock_utcnow):
    self._insert_selection(
        1,
        'foo/bar-baz',
        object_key='selections/wp1.selection.models.simple/1/My Builder.???')
    self._insert_builder()
    article_data = logic_builder.get_builders_with_selections(
        self.wp10db, '1234')
    self.assertObjectListsEqual(self.expected_lists_with_unmapped_selections,
                                article_data)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2020, 12, 25, 4, 44, 44))
  def test_get_builders_deleted_zim(self, mock_utcnow):
    self._insert_selection(1,
                           'text/tab-separated-values',
                           zim_file_ready=True,
                           version=1)
    self._insert_selection(2,
                           'text/tab-separated-values',
                           zim_file_ready=False,
                           version=2)
    self._insert_builder()
    article_data = logic_builder.get_builders_with_selections(
        self.wp10db, '1234')
    self.assertObjectListsEqual(self.expected_list_with_zimfarm_status,
                                article_data)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_get_builders_zimfarm_status(self, mock_utcnow):
    self._insert_selection(1,
                           'text/tab-separated-values',
                           zim_file_ready=True,
                           version=1)
    self._insert_selection(2,
                           'text/tab-separated-values',
                           zim_file_ready=False,
                           version=2)
    self._insert_builder()
    article_data = logic_builder.get_builders_with_selections(
        self.wp10db, '1234')
    self.assertObjectListsEqual(self.expected_list_with_zimfarm_status,
                                article_data)

  def test_update_builder_doesnt_exist(self):
    actual = logic_builder.update_builder(self.wp10db, self.builder)
    self.assertFalse(actual)

  def test_update_builder_user_id_doesnt_match(self):
    self._insert_builder()
    builder = Builder(
        b_id=b'1a-2b-3c-4d',
        b_name=b'My Builder',
        b_user_id=5555,  # Different user_id
        b_project=b'en.wikipedia.fake',
        b_model=b'wp1.selection.models.simple',
        b_params=b'{"list": ["a", "b", "c"]}',
    )
    actual = logic_builder.update_builder(self.wp10db, builder)
    self.assertFalse(actual)

  def test_update_builder_wrong_id(self):
    self._insert_builder()
    builder = Builder(
        b_id=b'100',  # Wrong ID
        b_name=b'My Builder',
        b_user_id=1234,
        b_project=b'en.wikipedia.fake',
        b_model=b'wp1.selection.models.simple',
        b_params=b'{"list": ["a", "b", "c"]}',
    )
    actual = logic_builder.update_builder(self.wp10db, builder)
    self.assertFalse(actual)

  def test_update_builder_success(self):
    self._insert_builder()
    builder = Builder(
        b_id=b'1a-2b-3c-4d',
        b_name=b'My Builder',
        b_user_id=1234,
        b_project=b'en.wikipedia.fake',
        b_model=b'wp1.selection.models.simple',
        b_params=b'{"list": ["a", "b", "c"]}',
    )
    actual = logic_builder.update_builder(self.wp10db, builder)
    self.assertTrue(actual)

  def test_update_builder_updates_fields(self):
    self._insert_builder()
    builder = Builder(b_id=b'1a-2b-3c-4d',
                      b_name=b'Builder 2',
                      b_user_id=1234,
                      b_project=b'zz.wikipedia.fake',
                      b_model=b'wp1.selection.models.complex',
                      b_params=b'{"list": ["1", "b", "c"]}',
                      b_created_at=b'20191225044444',
                      b_updated_at=b'20211111044444',
                      b_current_version=1,
                      b_selection_zim_version=1)
    actual = logic_builder.update_builder(self.wp10db, builder)
    self.assertTrue(actual)

    with self.wp10db.cursor() as cursor:
      cursor.execute('SELECT * FROM builders where b_id = %s', ('1a-2b-3c-4d',))
      db_builder = cursor.fetchone()
      actual_builder = Builder(**db_builder)
    self.assertEqual(builder, actual_builder)

  def test_latest_url_for(self):
    actual = logic_builder.latest_url_for(15, 'text/tab-separated-values')
    self.assertEqual(
        actual, 'http://test.server.fake/v1/builders/15/selection/latest.tsv')
    actual = logic_builder.latest_url_for(439, 'application/vnd.ms-excel')
    self.assertEqual(
        actual, 'http://test.server.fake/v1/builders/439/selection/latest.xls')

  def test_latest_url_for_unmapped_content_type(self):
    actual = logic_builder.latest_url_for(150, 'foo/bar-baz')
    self.assertIsNone(actual)

  @patch('wp1.logic.builder.CREDENTIALS', {})
  def test_latest_url_for_no_server_url(self):
    actual = logic_builder.latest_url_for(15, 'text/tab-separated-values')
    self.assertIsNone(actual)

  def test_latest_selection_url(self):
    builder_id = self._insert_builder()
    self._insert_selection(1, 'text/tab-separated-values')

    actual = logic_builder.latest_selection_url(self.wp10db, builder_id, 'tsv')

    self.assertEqual(
        actual,
        'http://credentials.not.found.fake/selections/foo/1234/name.tsv')

  def test_latest_selection_url_unknown_extension(self):
    builder_id = self._insert_builder()
    self._insert_selection(1, 'text/tab-separated-values')

    actual = logic_builder.latest_selection_url(self.wp10db, builder_id, 'foo')

    self.assertIsNone(actual)

  def test_latest_selection_url_missing_builder(self):
    builder_id = self._insert_builder()
    self._insert_selection(1, 'text/tab-separated-values')

    actual = logic_builder.latest_selection_url(self.wp10db, 'foo-bar-baz',
                                                'tsv')

    self.assertIsNone(actual)

  def test_latest_selection_url_missing_selection(self):
    builder_id = self._insert_builder()

    actual = logic_builder.latest_selection_url(self.wp10db, builder_id, 'tsv')

    self.assertIsNone(actual)

  def test_latest_selection_url_no_object_key(self):
    builder_id = self._insert_builder()
    self._insert_selection(1, 'text/tab-separated-values', object_key=None)

    actual = logic_builder.latest_selection_url(self.wp10db, builder_id, 'tsv')

    self.assertIsNone(actual)

  def test_latest_selection_url_unrelated_selections(self):
    builder_id = self._insert_builder()
    self._insert_selection(1, 'text/tab-separated-values', builder_id=-1)
    self._insert_selection(2, 'text/tab-separated-values', builder_id=-2)
    self._insert_selection(3, 'text/tab-separated-values', builder_id=-3)

    actual = logic_builder.latest_selection_url(self.wp10db, builder_id, 'tsv')

    self.assertIsNone(actual)

  def _insert_builder_with_multiple_version_selections(self):
    builder_id = self._insert_builder(current_version=3, zim_version=2)
    self._insert_selection(1,
                           'text/tab-separated-values',
                           version=1,
                           object_key='object_key_1',
                           builder_id=builder_id)
    self._insert_selection(2,
                           'application/vnd.ms-excel',
                           version=1,
                           object_key='object_key_2',
                           builder_id=builder_id)
    self._insert_selection(3,
                           'text/tab-separated-values',
                           version=2,
                           object_key='object_key_3',
                           builder_id=builder_id)
    self._insert_selection(4,
                           'text/tab-separated-values',
                           version=3,
                           object_key='proper/selection/4321/name.tsv',
                           builder_id=builder_id)

    return builder_id

  def test_latest_selection_url_multiple_versions(self):
    builder_id = self._insert_builder_with_multiple_version_selections()

    actual = logic_builder.latest_selection_url(self.wp10db, builder_id, 'tsv')

    self.assertEqual(
        actual,
        'http://credentials.not.found.fake/proper/selection/4321/name.tsv')

  @patch('wp1.logic.builder.zimfarm.zim_file_url_for_task_id',
         return_value='https://zim.fake/1234')
  def test_latest_zim_file_url_for(self, mock_zimfarm_url_for):
    builder_id = self._insert_builder_with_multiple_version_selections()
    with self.wp10db.cursor() as cursor:
      cursor.execute('''UPDATE zim_files z
                          INNER JOIN selections s ON s.s_id = z.z_selection_id
                          INNER JOIN builders b ON b.b_selection_zim_version = s.s_version
                        SET z_status = "FILE_READY"''')

    actual = logic_builder.latest_zim_file_url_for(self.wp10db, builder_id)

    self.assertEqual('https://zim.fake/1234', actual)

  @patch('wp1.logic.builder.zimfarm.zim_file_url_for_task_id',
         return_value='https://zim.fake/1234')
  def test_latest_zim_file_url_for_not_ready(self, mock_zimfarm_url_for):
    builder_id = self._insert_builder_with_multiple_version_selections()

    actual = logic_builder.latest_zim_file_url_for(self.wp10db, builder_id)

    self.assertIsNone(actual)

  @patch('wp1.logic.builder.logic_selection')
  def test_delete_builder(self, patched_selection):
    builder_id = self._insert_builder_with_multiple_version_selections()

    actual = logic_builder.delete_builder(self.wp10db, 1234, builder_id)

    self.assertTrue(actual['db_delete_success'])

  @patch('wp1.logic.builder.logic_selection')
  def test_delete_builder_user_id_unmatched(self, patched_selection):
    builder_id = self._insert_builder_with_multiple_version_selections()

    actual = logic_builder.delete_builder(self.wp10db, 4321, builder_id)

    self.assertFalse(actual['db_delete_success'])

  @patch('wp1.logic.builder.logic_selection')
  def test_delete_builder_user_builder_id_unmatched(self, patched_selection):
    builder_id = self._insert_builder_with_multiple_version_selections()

    actual = logic_builder.delete_builder(self.wp10db, 1234, 'abcd')

    self.assertFalse(actual['db_delete_success'])

  @patch('wp1.logic.builder.logic_selection')
  def test_delete_builder_user_no_selections(self, patched_selection):
    builder_id = self._insert_builder()

    actual = logic_builder.delete_builder(self.wp10db, 1234, builder_id)

    self.assertTrue(actual['db_delete_success'])

  @patch('wp1.logic.builder.logic_selection.delete_keys_from_storage')
  def test_delete_builder_deletes_object_keys(self, patched_delete_keys):
    builder_id = self._insert_builder_with_multiple_version_selections()
    patched_delete_keys.return_value = True

    actual = logic_builder.delete_builder(self.wp10db, 1234, builder_id)

    self.assertTrue(actual['db_delete_success'])
    self.assertTrue(actual['s3_delete_success'])
    patched_delete_keys.assert_called_once_with([
        b'object_key_1', b'object_key_2', b'object_key_3',
        b'proper/selection/4321/name.tsv'
    ])

  @patch('wp1.logic.builder.logic_selection.delete_keys_from_storage')
  def test_delete_builder_object_keys_missing(self, patched_delete_keys):
    builder_id = self._insert_builder_with_multiple_version_selections()
    patched_delete_keys.return_value = True

    self._insert_selection(5,
                           'application/vnd.ms-excel',
                           version=3,
                           object_key=None,
                           builder_id=builder_id)

    actual = logic_builder.delete_builder(self.wp10db, 1234, builder_id)

    self.assertTrue(actual['db_delete_success'])
    self.assertTrue(actual['s3_delete_success'])
    patched_delete_keys.assert_called_once_with([
        b'object_key_1', b'object_key_2', b'object_key_3',
        b'proper/selection/4321/name.tsv'
    ])

  def test_latest_selections_with_errors(self):
    builder_id = self._insert_builder(current_version=2)
    self._insert_selection(1,
                           'text/tab-separated-values',
                           version=1,
                           builder_id=builder_id,
                           has_errors=True)
    self._insert_selection(2,
                           'text/tab-separated-values',
                           version=2,
                           builder_id=builder_id,
                           has_errors=False)
    self._insert_selection(3,
                           'application/vnd.ms-excel',
                           version=2,
                           builder_id=builder_id,
                           has_errors=True)

    actual = logic_builder.latest_selections_with_errors(
        self.wp10db, builder_id)

    self.assertEqual([{
        'status': 'CAN_RETRY',
        'ext': 'xls',
        'error_messages': ['There was an error']
    }], actual)

  def test_latest_selection_with_errors_no_errors(self):
    builder_id = self._insert_builder()
    self._insert_selection(1,
                           'text/tab-separated-values',
                           builder_id=builder_id,
                           has_errors=False)
    self._insert_selection(2,
                           'application/vnd.ms-excel',
                           builder_id=builder_id,
                           has_errors=False)

    actual = logic_builder.latest_selections_with_errors(
        self.wp10db, builder_id)

    self.assertEqual(0, len(actual))

  @patch('wp1.logic.builder.zimfarm.schedule_zim_file')
  @patch('wp1.logic.builder.utcnow',
         return_value=datetime.datetime(2022, 12, 25, 0, 1, 2))
  def test_schedule_zim_file(self, patched_utcnow, patched_schedule_zim_file):
    redis = MagicMock()
    s3 = MagicMock()
    patched_schedule_zim_file.return_value = '1234-a'

    builder_id = self._insert_builder()
    self._insert_selection(1,
                           'text/tab-separated-values',
                           builder_id=builder_id,
                           has_errors=False)

    logic_builder.schedule_zim_file(s3,
                                    redis,
                                    self.wp10db,
                                    builder_id,
                                    user_id=1234,
                                    description='a',
                                    long_description='z')

    patched_schedule_zim_file.assert_called_once_with(s3,
                                                      redis,
                                                      self.wp10db,
                                                      self.builder,
                                                      description='a',
                                                      long_description='z')
    with self.wp10db.cursor() as cursor:
      cursor.execute('SELECT z_task_id, z_status, z_requested_at,'
                     '       z_description, z_long_description'
                     ' FROM zim_files'
                     ' WHERE z_selection_id = 1')
      data = cursor.fetchone()

    self.assertEqual(b'1234-a', data['z_task_id'])
    self.assertEqual(b'REQUESTED', data['z_status'])
    self.assertEqual(b'20221225000102', data['z_requested_at'])
    self.assertEqual(b'a', data['z_description'])
    self.assertEqual(b'z', data['z_long_description'])

  @patch('wp1.logic.builder.zimfarm.schedule_zim_file')
  def test_schedule_zim_file_404(self, patched_schedule_zim_file):
    redis = MagicMock()
    s3 = MagicMock()
    patched_schedule_zim_file.return_value = '1234-a'

    with self.assertRaises(ObjectNotFoundError):
      logic_builder.schedule_zim_file(s3,
                                      redis,
                                      self.wp10db,
                                      '404builder',
                                      user_id=1234)

  @patch('wp1.logic.builder.zimfarm.schedule_zim_file')
  def test_schedule_zim_file_not_authorized(self, patched_schedule_zim_file):
    redis = MagicMock()
    s3 = MagicMock()
    patched_schedule_zim_file.return_value = '1234-a'

    builder_id = self._insert_builder()
    self._insert_selection(1,
                           'text/tab-separated-values',
                           builder_id=builder_id,
                           has_errors=False)

    with self.assertRaises(UserNotAuthorizedError):
      logic_builder.schedule_zim_file(s3,
                                      redis,
                                      self.wp10db,
                                      builder_id,
                                      user_id=5678)

  @patch('wp1.logic.builder.zimfarm.is_zim_file_ready')
  @patch('wp1.logic.builder.wp10_connect')
  @patch('wp1.logic.builder.redis_connect')
  @patch('wp1.logic.selection.utcnow',
         return_value=datetime.datetime(2022, 12, 25, 0, 1, 2))
  def test_on_zim_file_status_poll_file_ready(self, patched_utcnow,
                                              patched_redis, patched_connect,
                                              patched_is_ready):
    patched_is_ready.return_value = 'FILE_READY'
    builder_id = self._insert_builder(zim_version=1)
    self._insert_selection(1,
                           'text/tab-separated-values',
                           version=1,
                           builder_id=builder_id,
                           has_errors=False,
                           zim_file_ready=True)
    self._insert_selection(2,
                           'text/tab-separated-values',
                           version=2,
                           builder_id=builder_id,
                           has_errors=False,
                           zim_task_id='9abc',
                           zim_file_ready=False)

    orig_close = self.wp10db.close
    try:
      self.wp10db.close = lambda: True
      patched_connect.return_value = self.wp10db
      logic_builder.on_zim_file_status_poll('9abc')
    finally:
      self.wp10db.close = orig_close

    with self.wp10db.cursor() as cursor:
      cursor.execute('SELECT z_status, z_updated_at '
                     'FROM zim_files WHERE z_selection_id = 2')
      data = cursor.fetchone()

    self.assertIsNotNone(data)
    self.assertEqual(b'FILE_READY', data['z_status'])
    self.assertEqual(b'20221225000102', data['z_updated_at'])

    with self.wp10db.cursor() as cursor:
      cursor.execute(
          'SELECT b.b_selection_zim_version FROM builders b '
          'WHERE b.b_id = %s', (builder_id,))
      zim_version = cursor.fetchone()['b_selection_zim_version']

    self.assertEqual(2, zim_version)

  @patch('wp1.logic.builder.utcnow',
         return_value=datetime.datetime(2023, 1, 1, 2, 30, 0, 0,
                                        datetime.timezone.utc))
  @patch('wp1.logic.builder.zimfarm.is_zim_file_ready')
  @patch('wp1.logic.builder.queues.poll_for_zim_file_status')
  @patch('wp1.logic.builder.wp10_connect')
  @patch('wp1.logic.builder.redis_connect')
  def test_on_zim_file_status_poll_requested(self, patched_redis,
                                             patched_connect,
                                             patched_poll_for_status,
                                             patched_is_ready, patched_utcnow):
    patched_is_ready.return_value = 'REQUESTED'
    builder_id = self._insert_builder()
    self._insert_selection(1,
                           'text/tab-separated-values',
                           builder_id=builder_id,
                           has_errors=False)

    orig_close = self.wp10db.close
    try:
      self.wp10db.close = lambda: True
      patched_connect.return_value = self.wp10db
      logic_builder.on_zim_file_status_poll('5678')
    finally:
      self.wp10db.close = orig_close

    patched_poll_for_status.assert_called_once()

  @patch('wp1.logic.builder.utcnow',
         return_value=datetime.datetime(2023, 1, 1, 5, 5, 5))
  @patch('wp1.logic.builder.zimfarm.is_zim_file_ready')
  @patch('wp1.logic.builder.queues.poll_for_zim_file_status')
  @patch('wp1.logic.builder.wp10_connect')
  @patch('wp1.logic.builder.redis_connect')
  def test_on_zim_file_status_poll_expired(self, patched_redis, patched_connect,
                                           patched_poll_for_status,
                                           patched_is_ready, patched_utcnow):
    patched_is_ready.return_value = 'REQUESTED'
    builder_id = self._insert_builder()
    self._insert_selection(1,
                           'text/tab-separated-values',
                           builder_id=builder_id,
                           has_errors=False)

    orig_close = self.wp10db.close
    try:
      self.wp10db.close = lambda: True
      patched_connect.return_value = self.wp10db
      logic_builder.on_zim_file_status_poll('5678')
    finally:
      self.wp10db.close = orig_close

    patched_poll_for_status.assert_not_called()

    with self.wp10db.cursor() as cursor:
      cursor.execute('SELECT z_status, z_updated_at '
                     'FROM zim_files WHERE z_selection_id = 1')
      data = cursor.fetchone()

    self.assertIsNotNone(data)
    self.assertEqual(b'FAILED', data['z_status'])
    self.assertIsNone(data['z_updated_at'])

  @patch('wp1.logic.builder.zimfarm.is_zim_file_ready')
  @patch('wp1.logic.builder.queues.poll_for_zim_file_status')
  @patch('wp1.logic.builder.wp10_connect')
  @patch('wp1.logic.builder.redis_connect')
  def test_on_zim_file_status_poll_failed(self, patched_redis, patched_connect,
                                          patched_poll_for_status,
                                          patched_is_ready):
    patched_is_ready.return_value = 'FAILED'
    builder_id = self._insert_builder()
    self._insert_selection(1,
                           'text/tab-separated-values',
                           builder_id=builder_id,
                           has_errors=False)

    orig_close = self.wp10db.close
    try:
      self.wp10db.close = lambda: True
      patched_connect.return_value = self.wp10db
      logic_builder.on_zim_file_status_poll('5678')
    finally:
      self.wp10db.close = orig_close

    with self.wp10db.cursor() as cursor:
      cursor.execute('SELECT z_status, z_updated_at '
                     'FROM zim_files WHERE z_selection_id = 1')
      data = cursor.fetchone()

    self.assertIsNotNone(data)
    self.assertEqual(b'FAILED', data['z_status'])
    self.assertIsNone(data['z_updated_at'])

  def test_update_version_for_finished_zim(self):
    builder_id = self._insert_builder(zim_version=1)
    self._insert_selection(1,
                           'text/tab-separated-values',
                           version=1,
                           builder_id=builder_id,
                           has_errors=False,
                           zim_file_ready=True)
    self._insert_selection(2,
                           'text/tab-separated-values',
                           version=2,
                           builder_id=builder_id,
                           has_errors=False,
                           zim_task_id='9abc',
                           zim_file_ready=True)

    logic_builder.update_version_for_finished_zim(self.wp10db, '9abc')

    with self.wp10db.cursor() as cursor:
      cursor.execute(
          'SELECT b.b_selection_zim_version '
          'FROM builders b WHERE b.b_id = %s', builder_id)
      data = cursor.fetchone()

    self.assertEqual(2, data['b_selection_zim_version'])

  @patch('wp1.logic.builder.schedule_zim_file')
  def test_auto_schedule_zim_file(self, patched_schedule_zim_file):
    s3 = MagicMock()
    redis = MagicMock()
    builder_id = self._insert_builder(zim_version=1)
    self._insert_selection(1,
                           'text/tab-separated-values',
                           version=1,
                           builder_id=builder_id,
                           has_errors=False,
                           zim_file_ready=True)

    logic_builder.auto_schedule_zim_file(s3, redis, self.wp10db, builder_id)

    patched_schedule_zim_file.assert_called_once_with(s3,
                                                      redis,
                                                      self.wp10db,
                                                      builder_id,
                                                      description=None,
                                                      long_description=None)

  @patch('wp1.logic.builder.schedule_zim_file')
  @patch('wp1.logic.builder.zimfarm.cancel_zim_by_task_id')
  def test_auto_schedule_zim_file_zimfarm_error(self, patched_cancel_zim,
                                                patched_schedule_zim_file):
    s3 = MagicMock()
    redis = MagicMock()
    patched_cancel_zim.side_effect = ZimFarmError
    builder_id = self._insert_builder(zim_version=1)
    self._insert_selection(1,
                           'text/tab-separated-values',
                           version=1,
                           builder_id=builder_id,
                           has_errors=False,
                           zim_file_ready=True)

    logic_builder.auto_schedule_zim_file(s3, redis, self.wp10db, builder_id)

    patched_schedule_zim_file.assert_called_once_with(s3,
                                                      redis,
                                                      self.wp10db,
                                                      builder_id,
                                                      description=None,
                                                      long_description=None)

  @patch('wp1.logic.builder.schedule_zim_file')
  @patch('wp1.logic.builder.zimfarm.cancel_zim_by_task_id')
  def test_auto_schedule_zim_file_cancel_tasks(self, patched_cancel_zim,
                                               patched_schedule_zim_file):
    s3 = MagicMock()
    redis = MagicMock()
    builder_id = self._insert_builder(zim_version=1)
    self._insert_selection(1,
                           'text/tab-separated-values',
                           version=1,
                           builder_id=builder_id,
                           has_errors=False,
                           zim_task_id='5678',
                           zim_file_ready=True)
    self._insert_selection(2,
                           'text/tab-separated-values',
                           version=2,
                           builder_id=builder_id,
                           has_errors=False,
                           zim_task_id='1abc',
                           zim_file_ready=False)
    self._insert_selection(3,
                           'text/tab-separated-values',
                           version=3,
                           builder_id=builder_id,
                           has_errors=False,
                           zim_task_id='9def',
                           zim_file_ready=False)

    with self.wp10db.cursor() as cursor:
      cursor.execute('''UPDATE zim_files z
                        JOIN selections s
                          ON s.s_id = z.z_selection_id
                        SET z.z_status = "REQUESTED"
                        WHERE s.s_id IN (2,3)''')
      cursor.execute('''UPDATE zim_files z
                        JOIN selections s
                          ON s.s_id = z.z_selection_id
                        SET z.z_description = "A desc", z.z_long_description = "Long desc"
                        WHERE s.s_id = 1''')

    logic_builder.auto_schedule_zim_file(s3, redis, self.wp10db, builder_id)

    patched_cancel_zim.assert_has_calls(
        (call(redis, '1abc'), call(redis, '9def')), any_order=True)

    patched_schedule_zim_file.assert_called_once_with(
        s3,
        redis,
        self.wp10db,
        builder_id,
        description='A desc',
        long_description='Long desc')

    with self.wp10db.cursor() as cursor:
      cursor.execute(
          'SELECT COUNT(*) as cnt FROM zim_files z WHERE z.z_status = "REQUESTED"'
      )
      count = cursor.fetchone()['cnt']

    self.assertEqual(0, count)

  def test_pending_zim_tasks_for(self):
    builder_id = self._insert_builder(zim_version=1)
    self._insert_selection(1,
                           'text/tab-separated-values',
                           version=1,
                           builder_id=builder_id,
                           has_errors=False,
                           zim_task_id='5678',
                           zim_file_ready=True)
    self._insert_selection(2,
                           'text/tab-separated-values',
                           version=2,
                           builder_id=builder_id,
                           has_errors=False,
                           zim_task_id='1abc',
                           zim_file_ready=False)
    self._insert_selection(3,
                           'text/tab-separated-values',
                           version=3,
                           builder_id=builder_id,
                           has_errors=False,
                           zim_task_id='9def',
                           zim_file_ready=False)

    with self.wp10db.cursor() as cursor:
      cursor.execute('''UPDATE zim_files z
                        JOIN selections s
                          ON s.s_id = z.z_selection_id
                        SET z.z_status = "REQUESTED"
                        WHERE s.s_id IN (2,3)''')

    tasks = logic_builder.pending_zim_tasks_for(self.wp10db, builder_id)
    self.assertIsNotNone(tasks)
    self.assertEqual(2, len(tasks))
    self.assertIn('1abc', tasks)
    self.assertIn('9def', tasks)
