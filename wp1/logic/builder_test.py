import datetime
from unittest.mock import patch, MagicMock, ANY

import attr

from wp1.base_db_test import BaseWpOneDbTest
from wp1.exceptions import ObjectNotFoundError, UserNotAuthorizedError
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
      's_zim_file_updated_at':
          None,
      's_zim_file_url':
          None,
      's_zimfarm_status':
          'NOT_REQUESTED',
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
          's_zim_file_updated_at':
              None,
          's_zim_file_url':
              None,
          's_zimfarm_status':
              'NOT_REQUESTED',
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
          's_zim_file_updated_at':
              None,
          's_zim_file_url':
              None,
          's_zimfarm_status':
              'NOT_REQUESTED',
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
      's_zim_file_updated_at': None,
      's_zim_file_url': None,
      's_zimfarm_status': None,
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
      's_zim_file_updated_at': None,
      's_zim_file_url': None,
      's_zimfarm_status': 'NOT_REQUESTED',
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
      's_zim_file_updated_at':
          1671927082,
      's_zim_file_url':
          'http://test.server.fake/v1/builders/1a-2b-3c-4d/zim/latest',
      's_zimfarm_status':
          'FILE_READY',
  }]

  def _insert_builder(self, current_version=None):
    if current_version is None:
      current_version = 1
    value_dict = attr.asdict(self.builder)
    value_dict['b_current_version'] = current_version
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

  def _insert_selection(self,
                        id_,
                        content_type,
                        version=1,
                        object_key='selections/foo/1234/name.tsv',
                        builder_id=b'1a-2b-3c-4d',
                        has_errors=False,
                        zim_file_ready=False):
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
                s_object_key, s_status, s_error_messages, s_zimfarm_task_id,
                s_zimfarm_status, s_zim_file_updated_at)
             VALUES
               (%s, %s, %s, "20191225044444", %s, %s, %s, %s, "5678", %s, %s)
          ''', (id_, builder_id, content_type, version, object_key, status,
                error_messages, zimfarm_status, zim_file_updated_at))
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
  def test_materialize(self, patched_connect_storage, patched_connect_wp10):
    patched_connect_wp10.return_value = self.wp10db
    TestBuilderClass = MagicMock()
    materialize_mock = MagicMock()
    TestBuilderClass.return_value = materialize_mock

    orig_close = self.wp10db.close
    try:
      self.wp10db.close = lambda: True
      id_ = self._insert_builder()

      logic_builder.materialize_builder(TestBuilderClass, id_,
                                        'text/tab-separated-values')
      materialize_mock.materialize.assert_called_once_with(
          ANY, ANY, self.builder, 'text/tab-separated-values')
    finally:
      self.wp10db.close = orig_close
    builder = self._get_builder_by_user_id()
    expected = dict(**self.expected_builder)
    expected['b_current_version'] = 1
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
  def test_get_builders_with_no_builders(self, mock_utcnow):
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
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_get_builders_zimfarm_status(self, mock_utcnow):
    self._insert_selection(1, 'text/tab-separated-values', zim_file_ready=True)
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
        b_id=1,
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
                      b_current_version=1)
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
    builder_id = self._insert_builder(current_version=3)
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
  def test_schedule_zim_file(self, patched_schedule_zim_file):
    redis = MagicMock()
    patched_schedule_zim_file.return_value = '1234-a'

    builder_id = self._insert_builder()
    self._insert_selection(1,
                           'text/tab-separated-values',
                           builder_id=builder_id,
                           has_errors=False)

    logic_builder.schedule_zim_file(redis, self.wp10db, 1234, builder_id)

    patched_schedule_zim_file.assert_called_once_with(redis, self.wp10db,
                                                      self.builder)
    with self.wp10db.cursor() as cursor:
      cursor.execute('SELECT s_zimfarm_task_id, s_zimfarm_status, '
                     ' s_zimfarm_error_messages FROM selections '
                     ' WHERE s_id = 1')
      data = cursor.fetchone()

    self.assertEqual(b'1234-a', data['s_zimfarm_task_id'])
    self.assertEqual(b'REQUESTED', data['s_zimfarm_status'])
    self.assertIsNone(data['s_zimfarm_error_messages'])

  @patch('wp1.logic.builder.zimfarm.schedule_zim_file')
  def test_schedule_zim_file(self, patched_schedule_zim_file):
    redis = MagicMock()
    patched_schedule_zim_file.return_value = '1234-a'

    with self.assertRaises(ObjectNotFoundError):
      logic_builder.schedule_zim_file(redis, self.wp10db, 1234, '404builder')

  @patch('wp1.logic.builder.zimfarm.schedule_zim_file')
  def test_schedule_zim_file(self, patched_schedule_zim_file):
    redis = MagicMock()
    patched_schedule_zim_file.return_value = '1234-a'

    builder_id = self._insert_builder()
    self._insert_selection(1,
                           'text/tab-separated-values',
                           builder_id=builder_id,
                           has_errors=False)

    with self.assertRaises(UserNotAuthorizedError):
      logic_builder.schedule_zim_file(redis, self.wp10db, 5678, builder_id)

  @patch('wp1.logic.builder.zimfarm.is_zim_file_ready')
  @patch('wp1.logic.builder.wp10_connect')
  @patch('wp1.logic.builder.redis_connect')
  @patch('wp1.logic.selection.utcnow',
         return_value=datetime.datetime(2022, 12, 25, 0, 1, 2))
  def test_on_zim_file_status_poll_true(self, patched_utcnow, patched_redis,
                                        patched_connect, patched_is_ready):
    patched_is_ready.return_value = True
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
      cursor.execute('SELECT s_zimfarm_status, s_zim_file_updated_at '
                     'FROM selections WHERE s_id = 1')
      data = cursor.fetchone()

    self.assertIsNotNone(data)
    self.assertEqual(b'FILE_READY', data['s_zimfarm_status'])
    self.assertEqual(b'20221225000102', data['s_zim_file_updated_at'])

  @patch('wp1.logic.builder.zimfarm.is_zim_file_ready')
  @patch('wp1.logic.builder.queues.poll_for_zim_file_status')
  @patch('wp1.logic.builder.wp10_connect')
  @patch('wp1.logic.builder.redis_connect')
  def test_on_zim_file_status_poll_false(self, patched_redis, patched_connect,
                                         patched_poll_for_status,
                                         patched_is_ready):
    patched_is_ready.return_value = False
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
