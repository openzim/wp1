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
