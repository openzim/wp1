from datetime import datetime

from lucky.base_db_test import BaseWpOneDbTest

import lucky.logic.release as logic_release
from lucky.models.wp10.release import Release

class ReleaseTest(BaseWpOneDbTest):

  def _get_all_releases(self):
    with self.wp10db.cursor() as cursor:
      cursor.execute('SELECT * FROM releases')
      db_releases = cursor.fetchall()
      return [Release(**db_release) for db_release in db_releases]

  def test_insert_or_update_release_data_insert(self):
    expected_dt = datetime.now()
    logic_release.insert_or_update_release_data(
      self.wp10db, b'Test Page', b'Test Category', expected_dt)
    actual = self._get_all_releases()
    self.assertEqual(1, len(actual))
    self.assertEqual(b'Test Page', actual[0].rel_article)
    self.assertEqual(b'Test Category', actual[0].rel_0p5_category)

  def test_insert_or_update_release_data_update(self):
    expected_dt = datetime.now()
    logic_release.insert_or_update_release_data(
      self.wp10db, b'Test Page', b'Test Category', expected_dt)
    logic_release.insert_or_update_release_data(
      self.wp10db, b'Test Page', b'Test Category 2', expected_dt)
    actual = self._get_all_releases()
    self.assertEqual(1, len(actual))
    self.assertEqual(b'Test Page', actual[0].rel_article)
    self.assertEqual(b'Test Category 2', actual[0].rel_0p5_category)

  def test_get_title_to_release(self):
    expected_dt = datetime.now()
    logic_release.insert_or_update_release_data(
      self.wp10db, b'Test Page 0', b'Test Category', expected_dt)
    logic_release.insert_or_update_release_data(
      self.wp10db, b'Test Page 1', b'Test Category 2', expected_dt)
    logic_release.insert_or_update_release_data(
      self.wp10db, b'Test Page 2', b'Test Category', expected_dt)
    logic_release.insert_or_update_release_data(
      self.wp10db, b'Test Page 3', b'Test Category 2', expected_dt)

    actual = logic_release.get_title_to_release(self.wp10db)
    self.assertEquals(4, len(actual))
    for expected_art in [b'Test Page %s' % str(i).encode('utf-8')
                         for i in range(4)]:
      self.assertTrue(expected_art in actual)

    self.assertEquals(b'Test Category', actual[b'Test Page 0'].rel_0p5_category)
    self.assertEquals(b'Test Category', actual[b'Test Page 2'].rel_0p5_category)
    self.assertEquals(
      b'Test Category 2', actual[b'Test Page 1'].rel_0p5_category)
    self.assertEquals(
      b'Test Category 2', actual[b'Test Page 3'].rel_0p5_category)
