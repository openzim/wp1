import datetime
from unittest.mock import patch, MagicMock, ANY

import attr

from wp1.base_db_test import BaseWpOneDbTest
from wp1.logic import builder as logic_builder
from wp1.models.wp10.builder import Builder
from wp1.selection.models.simple_builder import SimpleBuilder


class BuilderTest(BaseWpOneDbTest):

  builder = Builder(
      b_name=b'My Builder',
      b_user_id=1234,
      b_project=b'en.wikipedia.fake',
      b_model=b'wp1.selection.models.simple',
      b_params=b'{"list": ["a", "b", "c"]}',
      b_created_at=b'20191225044444',
      b_updated_at=b'20191225044444',
      b_current_version=1,
  )

  expected_builder = {
      'b_id': 1,
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
      'id': 1,
      'name': 'My Builder',
      'project': 'en.wikipedia.fake',
      'created_at': 1577249084,
      'updated_at': 1577249084,
      's_id': '1',
      's_updated_at': 1577249084,
      's_content_type': 'text/tab-separated-values',
      's_extension': 'tsv',
      's_url': 'http://credentials.not.found.fake/selections/foo/1234/name.tsv'
  }]

  expected_lists_with_multiple_selections = [{
      'id': 1,
      'name': 'My Builder',
      'project': 'en.wikipedia.fake',
      'created_at': 1577249084,
      'updated_at': 1577249084,
      's_id': '1',
      's_updated_at': 1577249084,
      's_content_type': 'text/tab-separated-values',
      's_extension': 'tsv',
      's_url': 'http://credentials.not.found.fake/object_key_1',
  }, {
      'id': 1,
      'name': 'My Builder',
      'project': 'en.wikipedia.fake',
      'created_at': 1577249084,
      'updated_at': 1577249084,
      's_id': '2',
      's_updated_at': 1577249084,
      's_content_type': 'application/vnd.ms-excel',
      's_extension': 'xls',
      's_url': 'http://credentials.not.found.fake/object_key_2',
  }]

  expected_lists_with_no_selections = [{
      'id': 1,
      'name': 'My Builder',
      'project': 'en.wikipedia.fake',
      'created_at': 1577249084,
      'updated_at': 1577249084,
      's_id': None,
      's_updated_at': None,
      's_content_type': None,
      's_extension': None,
      's_url': None,
  }]

  expected_lists_with_unmapped_selections = [{
      'id':
          1,
      'name':
          'My Builder',
      'project':
          'en.wikipedia.fake',
      'created_at':
          1577249084,
      'updated_at':
          1577249084,
      's_id':
          '1',
      's_updated_at':
          1577249084,
      's_content_type':
          'foo/bar-baz',
      's_extension':
          '???',
      's_url':
          'http://credentials.not.found.fake/selections/wp1.selection.models.simple/1/My%20Builder.%3F%3F%3F',
  }]

  def _insert_builder(self, version=None):
    if version is None:
      version = 1
    value_dict = attr.asdict(self.builder)
    value_dict['b_current_version'] = version
    with self.wp10db.cursor() as cursor:
      cursor.execute(
          '''INSERT INTO builders
         (b_name, b_user_id, b_project, b_params, b_model, b_created_at, b_updated_at,
         b_current_version)
         VALUES (%(b_name)s, %(b_user_id)s, %(b_project)s, %(b_params)s, %(b_model)s,
         %(b_created_at)s, %(b_updated_at)s, %(b_current_version)s)
        ''', value_dict)
      id_ = cursor.lastrowid
    self.wp10db.commit()
    return id_

  def _insert_selection(self,
                        id_,
                        content_type,
                        version=1,
                        object_key='selections/foo/1234/name.tsv'):
    with self.wp10db.cursor() as cursor:
      cursor.execute(
          'INSERT INTO selections VALUES (%s, 1, %s, "20191225044444", %s, %s)',
          (id_, content_type, version, object_key))
    self.wp10db.commit()

  def _get_builder_by_user_id(self):
    with self.wp10db.cursor() as cursor:
      cursor.execute('SELECT * FROM builders WHERE b_user_id=%(b_user_id)s',
                     {'b_user_id': '1234'})
      db_lists = cursor.fetchone()
      return db_lists

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_create_or_update_builder_create(self, mock_utcnow):
    logic_builder.create_or_update_builder(self.wp10db, 'My Builder', '1234',
                                           'en.wikipedia.fake', 'a\nb\nc')
    actual = self._get_builder_by_user_id()
    self.assertEqual(self.expected_builder, actual)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2020, 1, 1, 5, 55, 55))
  def test_create_or_update_builder_update(self, mock_utcnow):
    id_ = self._insert_builder()
    logic_builder.create_or_update_builder(self.wp10db, 'Builder 2', '1234',
                                           'zz.wikipedia.fake', 'a\nb\nc\nd',
                                           id_)
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
  def test_insert_builder(self, mock_utcnow):
    logic_builder.insert_builder(self.wp10db, self.builder)
    actual = self._get_builder_by_user_id()
    self.assertEqual(self.expected_builder, actual)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_insert_builder_returns_id(self, mock_utcnow):
    actual = logic_builder.insert_builder(self.wp10db, self.builder)
    self.assertEqual(1, actual)

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
    article_data = logic_builder.get_builders_with_selections(
        self.wp10db, '1234')
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
    article_data = logic_builder.get_builders_with_selections(
        self.wp10db, '1234')
    self.assertEqual(self.expected_lists_with_multiple_selections, article_data)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_get_builders_with_no_selections(self, mock_utcnow):
    self._insert_builder()
    article_data = logic_builder.get_builders_with_selections(
        self.wp10db, '1234')
    self.assertEqual(self.expected_lists_with_no_selections, article_data)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_get_builders_empty_lists(self, mock_utcnow):
    self._insert_selection(1, 'text/tab-separated-values')
    self._insert_builder()
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
    self._insert_builder()
    article_data = logic_builder.get_builders_with_selections(
        self.wp10db, '1234')
    self.assertEqual(self.expected_lists_with_multiple_selections, article_data)

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
    self.assertEqual(self.expected_lists_with_unmapped_selections, article_data)

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
        b_id=100,  # Wrong ID
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
        b_id=1,
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
    builder = Builder(b_id=1,
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
      cursor.execute('SELECT * FROM builders where b_id = %s', (1,))
      db_builder = cursor.fetchone()
      actual_builder = Builder(**db_builder)
    self.assertEqual(builder, actual_builder)
