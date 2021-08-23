from wp1.base_db_test import BaseWpOneDbTest
import wp1.logic.selection as logic_selection
from wp1.models.wp10.selection import Selection


def _get_selection(wp10db):
  with wp10db.cursor() as cursor:
    cursor.execute('SELECT * FROM selections LIMIT 1')
    db_selection = cursor.fetchone()
    return Selection(**db_selection)


class SelectionTest(BaseWpOneDbTest):

  def setUp(self):
    super().setUp()
    self.selection = Selection(s_id=b'deadbeef',
                               s_builder_id=100,
                               s_content_type=b'text/tab-separated-values',
                               s_updated_at=b'20190830112844')

  def test_insert_selection(self):
    logic_selection.insert_selection(self.wp10db, self.selection)
    actual = _get_selection(self.wp10db)
    self.assertEqual(self.selection, actual)

  def test_object_key_for_selection(self):
    actual = logic_selection.object_key_for_selection(self.selection,
                                                      'foo.bar.model')
    self.assertEqual('selections/foo.bar.model/deadbeef.tsv', actual)

  def test_object_key_for_selection_unknown_content_type(self):
    self.selection.s_content_type = b'foo/bar-baz'
    actual = logic_selection.object_key_for_selection(self.selection,
                                                      'foo.bar.model')
    self.assertEqual('selections/foo.bar.model/deadbeef.???', actual)

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
    self.assertEqual('selections/foo.bar.model/abcd-1234.tsv', actual)

  def test_object_key_for_none_selection_id(self):
    with self.assertRaises(ValueError):
      logic_selection.object_key_for(None, 'text/tab-separated-values',
                                     'foo.bar.model')

  def test_object_key_for_none_content_type(self):
    actual = logic_selection.object_key_for('abcd-1234', None, 'foo.bar.model')
    self.assertEqual('selections/foo.bar.model/abcd-1234.???', actual)

  def test_object_key_for_none_model(self):
    with self.assertRaises(ValueError):
      logic_selection.object_key_for('abcd-1234', 'text/tab-separated-values',
                                     None)
