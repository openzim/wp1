from lucky.base_orm_test import BaseWpOneOrmTest
from lucky.constants import AssessmentKind
from lucky.logic import rating as logic_rating
from lucky.models.wp10.log import Log
from lucky.models.wp10.rating import Rating


class LogicRatingTest(BaseWpOneOrmTest):
  def test_add_log_for_quality_rating(self):
    rating = Rating(
      project=b'Test Project', namespace=0, article=b'Testing Stuff',
      quality=b'GA-Class', quality_timestamp=b'2018-04-01T12:30:00Z')
    logic_rating.add_log_for_rating(
      self.session, rating, AssessmentKind.QUALITY, b'NotA-Class')
    self.session.commit()

    log = self.session.query(Log).filter(
      Log.article == b'Testing Stuff').first()
    self.assertIsNotNone(log)
    self.assertEqual(b'Test Project', log.project)
    self.assertEqual(0, log.namespace)
    self.assertEqual(b'Testing Stuff', log.article)
    self.assertEqual(b'GA-Class', log.new)
    self.assertEqual(b'NotA-Class', log.old)
    self.assertEqual(b'quality', log.action)

  def test_add_log_for_importance_rating(self):
    rating = Rating(
      project=b'Test Project', namespace=0, article=b'Testing Stuff',
      importance=b'Mid-Class', quality_timestamp=b'2018-04-01T12:30:00Z')
    logic_rating.add_log_for_rating(
      self.session, rating, AssessmentKind.IMPORTANCE, b'NotA-Class')
    self.session.commit()

    log = self.session.query(Log).filter(
      Log.article == b'Testing Stuff').first()
    self.assertIsNotNone(log)
    self.assertEqual(b'Test Project', log.project)
    self.assertEqual(0, log.namespace)
    self.assertEqual(b'Testing Stuff', log.article)
    self.assertEqual(b'Mid-Class', log.new)
    self.assertEqual(b'NotA-Class', log.old)
    self.assertEqual(b'importance', log.action)
