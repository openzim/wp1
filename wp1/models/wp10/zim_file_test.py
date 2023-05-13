import datetime
from unittest.mock import patch

from wp1.base_db_test import BaseWpOneDbTest
from wp1.models.wp10.zim_file import ZimFile


class ZimFileTest(BaseWpOneDbTest):

  def setUp(self):
    super().setUp()
    self.zim_file = ZimFile(z_id=1,
                            z_selection_id='deadbeef',
                            z_task_id='abcd-5678',
                            z_updated_at=b'20190830112844')

  def test_updated_at_dt(self):
    dt = self.zim_file.updated_at_dt
    self.assertEqual(2019, dt.year)
    self.assertEqual(8, dt.month)
    self.assertEqual(30, dt.day)
    self.assertEqual(11, dt.hour)
    self.assertEqual(28, dt.minute)
    self.assertEqual(44, dt.second)

  def test_set_updated_at_dt(self):
    dt = datetime.datetime(2020, 12, 15, 9, 30, 55)
    self.zim_file.set_updated_at_dt(dt)

    self.assertEqual(b'20201215093055', self.zim_file.z_updated_at)

  @patch('wp1.models.wp10.zim_file.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_set_updated_at_now(self, patched_now):
    self.zim_file.set_updated_at_now()

    self.assertEqual(b'20191225044444', self.zim_file.z_updated_at)
