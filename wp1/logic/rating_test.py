from wp1.base_db_test import BaseWpOneDbTest
from wp1.constants import AssessmentKind
from wp1.logic import rating as logic_rating
from wp1.models.wp10.log import Log
from wp1.models.wp10.rating import Rating


class LogicRatingTest(BaseWpOneDbTest):

  def test_add_log_for_quality_rating(self):
    rating = Rating(r_project=b'Test Project',
                    r_namespace=0,
                    r_article=b'Testing Stuff',
                    r_quality=b'GA-Class',
                    r_quality_timestamp=b'2018-04-01T12:30:00Z')
    logic_rating.add_log_for_rating(self.wp10db, rating, AssessmentKind.QUALITY,
                                    b'NotA-Class')

    with self.wp10db.cursor() as cursor:
      cursor.execute(
          '''
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
    rating = Rating(r_project=b'Test Project',
                    r_namespace=0,
                    r_article=b'Testing Stuff',
                    r_importance=b'Mid-Class',
                    r_importance_timestamp=b'2018-04-01T12:30:00Z')
    logic_rating.add_log_for_rating(self.wp10db, rating,
                                    AssessmentKind.IMPORTANCE, b'NotA-Class')

    with self.wp10db.cursor() as cursor:
      cursor.execute(
          '''
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


class GetProjectRatingByTypeTest(BaseWpOneDbTest):

  def _add_ratings(self, use_unassessed=False):
    qualities = ('FA-Class', 'A-Class', 'B-Class')
    if use_unassessed:
      qualities = qualities + ('Unassessed-Class',)
    ratings = []
    for i in range(25):
      for quality in ('FA-Class', 'A-Class', 'B-Class'):
        for importance in ('High-Class', 'Low-Class'):
          ratings.append({
              'r_project': 'Project 0',
              'r_namespace': 0,
              'r_article': '%s_%s_%s' % (quality, importance, i),
              'r_score': 0,
              'r_quality': quality,
              'r_quality_timestamp': '20191225T00:00:00',
              'r_importance': importance,
              'r_importance_timestamp': '20191226T00:00:00',
          })

    for i in range(1, 10):
      ratings.append({
          'r_project': 'Project %s' % i,
          'r_namespace': 0,
          'r_article': 'Fake_Article',
          'r_score': 0,
          'r_quality': 'FA-Class',
          'r_quality_timestamp': '20191225T00:00:00',
          'r_importance': 'High-Class',
          'r_importance_timestamp': '20191226T00:00:00',
      })

    with self.wp10db.cursor() as cursor:
      cursor.executemany(
          'INSERT INTO ratings '
          '(r_project, r_namespace, r_article, r_score, r_quality, '
          ' r_quality_timestamp, r_importance, r_importance_timestamp) '
          'VALUES '
          '(%(r_project)s, %(r_namespace)s, %(r_article)s, %(r_score)s, '
          ' %(r_quality)s, %(r_quality_timestamp)s, %(r_importance)s, '
          ' %(r_importance_timestamp)s)', ratings)
    self.wp10db.commit()

  def test_no_quality_or_importance(self):
    self._add_ratings()
    ratings = logic_rating.get_project_rating_by_type(self.wp10db, b'Project 0')

    # Currently limited to 100 results
    self.assertEqual(100, len(ratings))
    for rating in ratings:
      self.assertEqual(b'Project 0', rating.r_project)

  def test_quality(self):
    self._add_ratings()
    ratings = logic_rating.get_project_rating_by_type(self.wp10db,
                                                      b'Project 0',
                                                      quality=b'FA-Class')

    self.assertEqual(50, len(ratings))
    for rating in ratings:
      self.assertEqual(b'FA-Class', rating.r_quality)

  def test_importance(self):
    self._add_ratings()
    ratings = logic_rating.get_project_rating_by_type(self.wp10db,
                                                      b'Project 0',
                                                      importance=b'High-Class')

    self.assertEqual(75, len(ratings))
    for rating in ratings:
      self.assertEqual(b'High-Class', rating.r_importance)

  def test_no_results(self):
    self._add_ratings()
    ratings = logic_rating.get_project_rating_by_type(self.wp10db,
                                                      b'Project 0',
                                                      importance=b'Foo-Class')
    self.assertEqual(0, len(ratings))

    ratings = logic_rating.get_project_rating_by_type(self.wp10db,
                                                      b'Project 0',
                                                      quality=b'Bar-Class')
    self.assertEqual(0, len(ratings))

    ratings = logic_rating.get_project_rating_by_type(self.wp10db,
                                                      b'Project 0',
                                                      quality=b'Foo-Class',
                                                      importance=b'Bar-Class')
    self.assertEqual(0, len(ratings))

  def test_sorted_by_quality(self):
    self._add_ratings()
    ratings = logic_rating.get_project_rating_by_type(self.wp10db,
                                                      b'Project 0',
                                                      importance=b'High-Class')

    self.assertEqual(75, len(ratings))
    for rating in ratings[:25]:
      self.assertEqual(b'FA-Class', rating.r_quality)
    for rating in ratings[25:50]:
      self.assertEqual(b'A-Class', rating.r_quality)
    for rating in ratings[50:]:
      self.assertEqual(b'B-Class', rating.r_quality)

  def test_sorted_by_importance(self):
    self._add_ratings()
    ratings = logic_rating.get_project_rating_by_type(self.wp10db,
                                                      b'Project 0',
                                                      quality=b'FA-Class')

    self.assertEqual(50, len(ratings))
    for rating in ratings[:25]:
      self.assertEqual(b'High-Class', rating.r_importance)
    for rating in ratings[25:50]:
      self.assertEqual(b'Low-Class', rating.r_importance)

  def test_overall_sort_and_paging(self):
    self._add_ratings()
    ratings = logic_rating.get_project_rating_by_type(self.wp10db, b'Project 0')

    self.assertEqual(100, len(ratings))
    for rating in ratings[:25]:
      self.assertEqual(b'FA-Class', rating.r_quality)
      self.assertEqual(b'High-Class', rating.r_importance)
    for rating in ratings[25:50]:
      self.assertEqual(b'FA-Class', rating.r_quality)
      self.assertEqual(b'Low-Class', rating.r_importance)
    for rating in ratings[50:75]:
      self.assertEqual(b'A-Class', rating.r_quality)
      self.assertEqual(b'High-Class', rating.r_importance)
    for rating in ratings[75:]:
      self.assertEqual(b'A-Class', rating.r_quality)
      self.assertEqual(b'Low-Class', rating.r_importance)

    ratings = logic_rating.get_project_rating_by_type(self.wp10db,
                                                      b'Project 0',
                                                      page=2)

    self.assertEqual(50, len(ratings))
    for rating in ratings[:25]:
      self.assertEqual(b'B-Class', rating.r_quality)
      self.assertEqual(b'High-Class', rating.r_importance)
    for rating in ratings[25:50]:
      self.assertEqual(b'B-Class', rating.r_quality)
      self.assertEqual(b'Low-Class', rating.r_importance)

  def test_assessed_class(self):
    self._add_ratings(use_unassessed=True)
    ratings = logic_rating.get_project_rating_by_type(self.wp10db,
                                                      b'Project 0',
                                                      quality=b'Assessed-Class')

    self.assertEqual(100, len(ratings))
    for rating in ratings:
      self.assertNotEqual(b'Unassessed-Class', rating.r_quality)

    ratings = logic_rating.get_project_rating_by_type(self.wp10db,
                                                      b'Project 0',
                                                      quality=b'Assessed-Class',
                                                      page=2)

    self.assertEqual(50, len(ratings))
    for rating in ratings:
      self.assertNotEqual(b'Unassessed-Class', rating.r_quality)
