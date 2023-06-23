from unittest.mock import patch, MagicMock

import attr

from wp1.base_db_test import BaseWpOneDbTest
import wp1.logic.selection as logic_selection
from wp1.models.wp10.selection import Selection
from wp1.models.wp10.zim_file import ZimFile


def _get_selection(wp10db):
  with wp10db.cursor() as cursor:
    cursor.execute('SELECT * FROM selections LIMIT 1')
    db_selection = cursor.fetchone()
    return Selection(**db_selection)


def _get_zim_file_for_selection(wp10db, selection_id):
  with wp10db.cursor() as cursor:
    cursor.execute('SELECT * FROM zim_files WHERE z_selection_id = %s LIMIT 1',
                   (selection_id,))
    db_zim_file = cursor.fetchone()
    return ZimFile(**db_zim_file)


class SelectionTest(BaseWpOneDbTest):

  def setUp(self):
    super().setUp()
    self.selection = Selection(
        s_id=b'deadbeef',
        s_builder_id=b'100',
        s_content_type=b'text/tab-separated-values',
        s_version=1,
        s_updated_at=b'20190830112844',
        s_object_key=b'selections/foo.bar.model/deadbeef/name.tsv',
    )
    self.zim_file = ZimFile(z_id=1,
                            z_selection_id=b'deadbeef',
                            z_status=b'NOT_REQUESTED',
                            z_task_id=b'xyz1',
                            z_requested_at=b'20230101020202')

  def _insert_selections(self, selections=None, zim_files=None):
    if selections is None:
      selections = [self.selection]
    if zim_files is None:
      zim_files = [self.zim_file]
    selections = [attr.asdict(s) for s in selections]
    zim_files = [attr.asdict(z) for z in zim_files]

    with self.wp10db.cursor() as cursor:
      cursor.executemany(
          '''INSERT INTO selections
              (s_id, s_builder_id, s_version, s_content_type, s_updated_at,
               s_object_key)
             VALUES
              (%(s_id)s, %(s_builder_id)s, %(s_version)s, %(s_content_type)s,
               %(s_updated_at)s, %(s_object_key)s)
           ''', selections)
      cursor.executemany(
          '''INSERT INTO zim_files
             (z_id, z_selection_id, z_status, z_task_id, z_requested_at)
           VALUES
             (%(z_id)s, %(z_selection_id)s, %(z_status)s, %(z_task_id)s,
              %(z_requested_at)s)
          ''', zim_files)
    self.wp10db.commit()

  def test_insert_selection(self):
    logic_selection.insert_selection(self.wp10db, self.selection)
    actual = _get_selection(self.wp10db)
    expected_zim = ZimFile(z_id=1, z_selection_id=self.selection.s_id)
    actual_zim = _get_zim_file_for_selection(self.wp10db, self.selection.s_id)
    self.assertEqual(self.selection, actual)
    self.assertEqual(expected_zim, actual_zim)

  def test_get_next_version_empty_table(self):
    actual = logic_selection.get_next_version(self.wp10db, 100,
                                              b'text/tab-separated-values')
    self.assertEqual(1, actual)

  def test_get_next_version_no_builder_match(self):
    self._insert_selections()
    actual = logic_selection.get_next_version(self.wp10db, 200,
                                              b'text/tab-separated-values')
    self.assertEqual(1, actual)

  def test_get_next_version_no_content_match(self):
    self._insert_selections()
    actual = logic_selection.get_next_version(self.wp10db, 100,
                                              b'foo/content-type')
    self.assertEqual(1, actual)

  def test_get_next_version_existing_content(self):
    self._insert_selections()
    actual = logic_selection.get_next_version(self.wp10db, 100,
                                              b'text/tab-separated-values')
    self.assertEqual(2, actual)

  def test_get_next_version_balanced_versions(self):
    self._insert_selections(selections=[
        Selection(s_id=b'deadbeef',
                  s_builder_id=100,
                  s_content_type=b'text/tab-separated-values',
                  s_version=1,
                  s_updated_at=b'20190830112844',
                  s_object_key=b'object_key'),
        Selection(s_id=b'beefdead',
                  s_builder_id=100,
                  s_content_type=b'application/vnd.ms-excel',
                  s_version=1,
                  s_updated_at=b'20190830112844',
                  s_object_key=b'object_key'),
        Selection(s_id=b'dead0000',
                  s_builder_id=100,
                  s_content_type=b'text/tab-separated-values',
                  s_version=2,
                  s_updated_at=b'20190830112844',
                  s_object_key=b'object_key'),
        Selection(s_id=b'0000beef',
                  s_builder_id=100,
                  s_content_type=b'application/vnd.ms-excel',
                  s_version=2,
                  s_updated_at=b'20190830112844',
                  s_object_key=b'object_key'),
    ])
    actual = logic_selection.get_next_version(self.wp10db, 100,
                                              b'text/tab-separated-values')
    self.assertEqual(3, actual)

  def test_get_next_version_unbalanced_versions(self):
    self._insert_selections(selections=[
        Selection(s_id=b'deadbeef',
                  s_builder_id=100,
                  s_content_type=b'text/tab-separated-values',
                  s_version=1,
                  s_updated_at=b'20190830112844',
                  s_object_key=b'object_key'),
        Selection(s_id=b'beefdead',
                  s_builder_id=100,
                  s_content_type=b'application/vnd.ms-excel',
                  s_version=1,
                  s_updated_at=b'20190830112844',
                  s_object_key=b'object_key'),
        Selection(s_id=b'0000beef',
                  s_builder_id=100,
                  s_content_type=b'application/vnd.ms-excel',
                  s_version=2,
                  s_updated_at=b'20190830112844',
                  s_object_key=b'object_key'),
    ])
    actual = logic_selection.get_next_version(self.wp10db, 100,
                                              b'text/tab-separated-values')
    self.assertEqual(2, actual)

  def test_object_key_for_selection(self):
    actual = logic_selection.object_key_for_selection(self.selection,
                                                      'foo.bar.model')
    self.assertEqual('selections/foo.bar.model/deadbeef/selection.tsv', actual)

  def test_object_key_for_selection_unknown_content_type(self):
    self.selection.s_content_type = b'foo/bar-baz'
    actual = logic_selection.object_key_for_selection(self.selection,
                                                      'foo.bar.model')
    self.assertEqual('selections/foo.bar.model/deadbeef/selection.???', actual)

  def test_object_key_for_selection_none_selection(self):
    with self.assertRaises(ValueError):
      logic_selection.object_key_for_selection(None, 'foo.bar.model')

  def test_object_key_for_selection_none_model(self):
    with self.assertRaises(ValueError):
      logic_selection.object_key_for_selection(self.selection, None)

  def test_object_key_for(self):
    actual = logic_selection.object_key_for('abcd-1234',
                                            'text/tab-separated-values',
                                            'foo.bar.model')
    self.assertEqual('selections/foo.bar.model/abcd-1234/selection.tsv', actual)

  def test_object_key_for_none_selection_id(self):
    with self.assertRaises(ValueError):
      logic_selection.object_key_for(None, 'text/tab-separated-values',
                                     'foo.bar.model')

  def test_object_key_for_none_content_type(self):
    actual = logic_selection.object_key_for('abcd-1234', None, 'foo.bar.model')
    self.assertEqual('selections/foo.bar.model/abcd-1234/selection.???', actual)

  def test_object_key_for_none_model(self):
    with self.assertRaises(ValueError):
      logic_selection.object_key_for('abcd-1234', 'text/tab-separated-values',
                                     None)

  def test_url_for_selection(self):
    actual = logic_selection.url_for_selection(self.selection)
    self.assertEqual(
        'http://credentials.not.found.fake/selections/foo.bar.model/deadbeef/name.tsv',
        actual)

  def test_url_for_selection_none_selection(self):
    with self.assertRaises(ValueError):
      logic_selection.url_for_selection(None)

  def test_url_for(self):
    actual = logic_selection.url_for(
        'selections/foo.bar.model/abcd-1234/selection.tsv')
    self.assertEqual(
        'http://credentials.not.found.fake/selections/foo.bar.model/abcd-1234/selection.tsv',
        actual)

  def test_url_for_bytes(self):
    actual = logic_selection.url_for(
        b'selections/foo.bar.model/abcd-1234/selection.tsv')
    self.assertEqual(
        'http://credentials.not.found.fake/selections/foo.bar.model/abcd-1234/selection.tsv',
        actual)

  def test_url_for_none_object_id(self):
    with self.assertRaises(ValueError):
      logic_selection.url_for(None)

  def test_url_for_escapes(self):
    actual = logic_selection.url_for(
        'selections/foo.bar.model/abcd-1234/Héllo Wørld.???')
    self.assertEqual(
        'http://credentials.not.found.fake/selections/foo.bar.model/abcd-1234/'
        'H%C3%A9llo%20W%C3%B8rld.%3F%3F%3F', actual)

  def test_object_key_for_selection_with_name(self):
    actual = logic_selection.object_key_for_selection(self.selection,
                                                      'foo.bar.model',
                                                      name='name')
    self.assertEqual('selections/foo.bar.model/deadbeef/name.tsv', actual)

  def test_object_key_for_selection_with_name_and_legacy_schema(self):
    actual = logic_selection.object_key_for_selection(self.selection,
                                                      'foo.bar.model',
                                                      name='name',
                                                      use_legacy_schema=True)
    self.assertEqual('selections/foo.bar.model/deadbeef.tsv', actual)

  def test_object_key_for_selection_unknown_content_type_and_name(self):
    self.selection.s_content_type = b'foo/bar-baz'
    actual = logic_selection.object_key_for_selection(self.selection,
                                                      'foo.bar.model',
                                                      name='name')
    self.assertEqual('selections/foo.bar.model/deadbeef/name.???', actual)

  def test_object_key_for(self):
    actual = logic_selection.object_key_for('abcd-1234',
                                            'text/tab-separated-values',
                                            'foo.bar.model',
                                            name='name')
    self.assertEqual('selections/foo.bar.model/abcd-1234/name.tsv', actual)

  def test_object_key_for_none_content_type_and_name(self):
    actual = logic_selection.object_key_for('abcd-1234',
                                            None,
                                            'foo.bar.model',
                                            name='name')
    self.assertEqual('selections/foo.bar.model/abcd-1234/name.???', actual)

  @patch('wp1.logic.selection.connect_storage')
  def test_delete_keys_from_storage(self, patched_connect_storage):
    s3 = MagicMock()
    bucket = MagicMock()
    patched_connect_storage.return_value = s3
    s3.bucket = bucket

    actual = logic_selection.delete_keys_from_storage(
        [b'object/key/1', b'object/key/2'])

    bucket.delete_objects.assert_called_once_with(
        Delete={
            'Objects': [{
                'Key': 'object/key/1'
            }, {
                'Key': 'object/key/2'
            }],
            'Quiet': True
        })
    self.assertTrue(actual)

  @patch('wp1.logic.selection.connect_storage')
  def test_delete_keys_from_storage_single_bytes(self, patched_connect_storage):
    s3 = MagicMock()
    bucket = MagicMock()
    patched_connect_storage.return_value = s3
    s3.bucket = bucket

    actual = logic_selection.delete_keys_from_storage(b'object/key/1')

    bucket.delete_objects.assert_called_once_with(Delete={
        'Objects': [{
            'Key': 'object/key/1'
        }],
        'Quiet': True
    })
    self.assertTrue(actual)

  @patch('wp1.logic.selection.connect_storage')
  def test_delete_keys_from_storage_single_str(self, patched_connect_storage):
    s3 = MagicMock()
    bucket = MagicMock()
    patched_connect_storage.return_value = s3
    s3.bucket = bucket

    with self.assertRaises(ValueError):
      logic_selection.delete_keys_from_storage('object/key/1')

  @patch('wp1.logic.selection.connect_storage')
  def test_delete_keys_from_storage_list_of_str(self, patched_connect_storage):
    s3 = MagicMock()
    bucket = MagicMock()
    patched_connect_storage.return_value = s3
    s3.bucket = bucket

    with self.assertRaises(ValueError):
      logic_selection.delete_keys_from_storage(['object/key/1', 'object/key/2'])

  @patch('wp1.logic.selection.connect_storage')
  def test_delete_keys_from_storage_mix_of_str_and_bytes(
      self, patched_connect_storage):
    s3 = MagicMock()
    bucket = MagicMock()
    patched_connect_storage.return_value = s3
    s3.bucket = bucket

    with self.assertRaises(ValueError):
      logic_selection.delete_keys_from_storage(
          [b'object/key/1', 'object/key/2'])

  def test_zim_file_requested_at_for(self):
    self._insert_selections()
    actual = logic_selection.zim_file_requested_at_for(self.wp10db, 'xyz1')
    self.assertEqual(1672538522, actual)

  def test_get_resource_profile(self):
    s3 = MagicMock()
    s3.client.head_object.return_value = {'ContentLength': 20000000}
    selection = Selection(s_builder_id=b'abcd',
                          s_content_type=b'text/tab-separated-values',
                          s_version=1,
                          s_object_key=b'foo/bar/1234.tsv')
    actual = logic_selection.get_resource_profile(s3, selection)
    self.assertEqual({
        'cpu': 3,
        'disk': 42949672960,
        'memory': 6442450944
    }, actual)
