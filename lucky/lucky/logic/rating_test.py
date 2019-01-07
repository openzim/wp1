from lucky.base_db_test import BaseWpOneDbTest
from lucky.constants import AssessmentKind
from lucky.db_util import get_cursor_context
from lucky.logic import rating as logic_rating
from lucky.models.wp10.log import Log
from lucky.models.wp10.rating import Rating


class LogicRatingTest(BaseWpOneDbTest):
  def test_add_log_for_quality_rating(self):
    rating = Rating(
      r_project=b'Test Project', r_namespace=0, r_article=b'Testing Stuff',
      r_quality=b'GA-Class', r_quality_timestamp=b'2018-04-01T12:30:00Z')
    logic_rating.add_log_for_rating(
      self.wp10db, rating, AssessmentKind.QUALITY, b'NotA-Class')

    with get_cursor_context(self.wp10db) as cursor:
      cursor.execute('''
        SELECT * FROM ''' + Log.table_name + '''
        WHERE l_article = %s
      ''', (b'Testing Stuff',))
      db_log = cursor.fetchone()
      self.assertIsNotNone(db_log)
      log = Log(**db_log)
    self.assertEqual(b'Test Project', log.l_project)
    self.assertEqual(0, log.l_namespace)
    self.assertEqual(b'Testing Stuff', log.l_article)
    self.assertEqual(b'GA-Class', log.l_new)
    self.assertEqual(b'NotA-Class', log.l_old)
    self.assertEqual(b'quality', log.l_action)

  def test_add_log_for_importance_rating(self):
    rating = Rating(
      r_project=b'Test Project', r_namespace=0, r_article=b'Testing Stuff',
      r_importance=b'Mid-Class',
      r_importance_timestamp=b'2018-04-01T12:30:00Z')
    logic_rating.add_log_for_rating(
      self.wp10db, rating, AssessmentKind.IMPORTANCE, b'NotA-Class')

    with get_cursor_context(self.wp10db) as cursor:
      cursor.execute('''
        SELECT * FROM ''' + Log.table_name + '''
        WHERE l_article = %s
      ''', (b'Testing Stuff',))
      db_log = cursor.fetchone()
      self.assertIsNotNone(db_log)
      log = Log(**db_log)
    self.assertEqual(b'Test Project', log.l_project)
    self.assertEqual(0, log.l_namespace)
    self.assertEqual(b'Testing Stuff', log.l_article)
    self.assertEqual(b'Mid-Class', log.l_new)
    self.assertEqual(b'NotA-Class', log.l_old)
    self.assertEqual(b'importance', log.l_action)
