import datetime
from unittest.mock import patch

from wp1.base_db_test import BaseWpOneDbTest
from wp1.models.wp10.selection import Selection


class ModelsSelectionTest(BaseWpOneDbTest):

  def setUp(self):
    super().setUp()
    self.selection = Selection(s_name='My List',
                               s_user_id=100,
                               s_project='en.wikipedia.org',
                               s_last_generated=b'20180929123055')

  def test_last_generated_dt(self):
    dt = self.selection.last_generated_dt
    self.assertEqual(2018, dt.year)
    self.assertEqual(9, dt.month)
    self.assertEqual(29, dt.day)
    self.assertEqual(12, dt.hour)
    self.assertEqual(30, dt.minute)
    self.assertEqual(55, dt.second)

  def test_set_last_generated_dt(self):
    dt = datetime.datetime(2020, 12, 15, 9, 30, 55)
    self.selection.set_last_generated_dt(dt)

    self.assertEqual(b'20201215093055', self.selection.s_last_generated)

  @patch('wp1.models.wp10.selection.utcnow',
         return_value=datetime.datetime(2018, 12, 25, 5, 55, 55))
  def test_set_last_generated_now(self, patched_now):
    self.selection.set_last_generated_now()

    self.assertEqual(b'20181225055555', self.selection.s_last_generated)
