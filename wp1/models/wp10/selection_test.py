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
                               s_last_generated=b'2018-09-29T12:30:55Z',
                               s_created_at=b'2018-09-29T12:30:55Z',
                               s_model=b'org.fakemodel')

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

    self.assertEqual(b'2020-12-15T09:30:55Z', self.selection.s_last_generated)

  @patch('wp1.models.wp10.selection.utcnow',
         return_value=datetime.datetime(2018, 12, 25, 5, 55, 55))
  def test_set_last_generated_now(self, patched_now):
    self.selection.set_last_generated_now()

    self.assertEqual(b'2018-12-25T05:55:55Z', self.selection.s_last_generated)

  def test_created_at_dt(self):
    dt = self.selection.created_at_dt
    self.assertEqual(2018, dt.year)
    self.assertEqual(9, dt.month)
    self.assertEqual(29, dt.day)
    self.assertEqual(12, dt.hour)
    self.assertEqual(30, dt.minute)
    self.assertEqual(55, dt.second)

  def test_set_created_at_dt(self):
    dt = datetime.datetime(2020, 12, 15, 9, 30, 55)
    self.selection.set_created_at_dt(dt)

    self.assertEqual(b'2020-12-15T09:30:55Z', self.selection.s_created_at)

  @patch('wp1.models.wp10.selection.utcnow',
         return_value=datetime.datetime(2018, 12, 25, 5, 55, 55))
  def test_set_created_at_now(self, patched_now):
    self.selection.set_created_at_now()

    self.assertEqual(b'2018-12-25T05:55:55Z', self.selection.s_created_at)

  def test_calculate_from_id_object_key_equal(self):
    self.selection.calculate_from_id(1234)
    expected = b'selections/org.fakemodel/100/%s.tsv' % self.selection.s_hash
    self.assertEqual(expected, self.selection.s_object_key)

  def test_calculate_from_id_hash_set(self):
    self.selection.calculate_from_id(1234)
    self.assertIsNotNone(self.selection.s_hash)

  def test_calculate_from_id_id_equal(self):
    self.selection.calculate_from_id(1234)
    self.assertEqual(1234, self.selection.s_id)

  def test_calculate_from_id_raises_if_no_id(self):
    self.assertRaises(ValueError,
                      lambda: self.selection.calculate_from_id(None))

  def test_calculate_from_id_raises_if_no_model(self):
    self.selection.s_model = None
    self.assertRaises(ValueError,
                      lambda: self.selection.calculate_from_id(1234))

  def test_calculate_from_id_raises_if_no_user_id(self):
    self.selection.s_user_id = None
    self.assertRaises(ValueError,
                      lambda: self.selection.calculate_from_id(1234))
