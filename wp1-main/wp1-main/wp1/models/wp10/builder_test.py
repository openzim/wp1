import datetime
from unittest.mock import patch

from wp1.base_db_test import BaseWpOneDbTest
from wp1.models.wp10.builder import Builder


class ModelsBuilderTest(BaseWpOneDbTest):

  def setUp(self):
    super().setUp()
    self.builder = Builder(b_name='My List',
                           b_user_id=100,
                           b_project='en.wikipedia.org',
                           b_model='wp1.selection.models.simple',
                           b_params='{}',
                           b_created_at=b'20180929123055',
                           b_updated_at=b'20190830112844')

  def test_created_at_dt(self):
    dt = self.builder.created_at_dt
    self.assertEqual(2018, dt.year)
    self.assertEqual(9, dt.month)
    self.assertEqual(29, dt.day)
    self.assertEqual(12, dt.hour)
    self.assertEqual(30, dt.minute)
    self.assertEqual(55, dt.second)

  def test_set_created_at_dt(self):
    dt = datetime.datetime(2020, 12, 15, 9, 30, 55)
    self.builder.set_created_at_dt(dt)

    self.assertEqual(b'20201215093055', self.builder.b_created_at)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2018, 12, 25, 5, 55, 55))
  def test_set_created_at_now(self, patched_now):
    self.builder.set_created_at_now()

    self.assertEqual(b'20181225055555', self.builder.b_created_at)

  def test_updated_at_dt(self):
    dt = self.builder.updated_at_dt
    self.assertEqual(2019, dt.year)
    self.assertEqual(8, dt.month)
    self.assertEqual(30, dt.day)
    self.assertEqual(11, dt.hour)
    self.assertEqual(28, dt.minute)
    self.assertEqual(44, dt.second)

  def test_set_updated_at_dt(self):
    dt = datetime.datetime(2020, 12, 15, 9, 30, 55)
    self.builder.set_updated_at_dt(dt)

    self.assertEqual(b'20201215093055', self.builder.b_updated_at)

  @patch('wp1.models.wp10.builder.utcnow',
         return_value=datetime.datetime(2019, 12, 25, 4, 44, 44))
  def test_set_updated_at_now(self, patched_now):
    self.builder.set_updated_at_now()

    self.assertEqual(b'20191225044444', self.builder.b_updated_at)
