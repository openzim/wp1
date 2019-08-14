import unittest

import attr

from lucky import tables
from lucky.base_db_test import BaseWpOneDbTest
from lucky.constants import AssessmentKind, CATEGORY_NS_INT, GLOBAL_TIMESTAMP_WIKI, TS_FORMAT
from lucky.models.wp10.rating import Rating

class TablesCategoryTest(unittest.TestCase):
  GLOBAL_SORT_QUAL = {
    b'FA-Class':     500,
    b'FL-Class':     480,
    b'A-Class':      425, 
    b'GA-Class':     400,
    b'B-Class':      300,
    b'C-Class':      225, 
    b'Start-Class':  150,
    b'Stub-Class':   100,
    b'List-Class':    80, 
    tables.ASSESSED_CLASS:   20,
    tables.NOT_A_CLASS:      11,
    b'Unknown-Class': 10,
    tables.UNASSESSED_CLASS:  0,
  }

  GLOBAL_SORT_IMP = {
    b'Top-Class':    400,
    b'High-Class':   300, 
    b'Mid-Class':    200,
    b'Low-Class':    100, 
    tables.NOT_A_CLASS:      11,
    b'Unknown-Class': 10,
    tables.UNASSESSED_CLASS:  0,
  }

  def test_commas(self):
    actual = tables.commas(1200300)
    self.assertEqual('1,200,300', actual)

  def test_commas_small_number(self):
    actual = tables.commas(123)
    self.assertEqual('123', actual)

  def test_labels_for_classes(self):
    actual_qual, actual_imp = tables.labels_for_classes(
      self.GLOBAL_SORT_QUAL, self.GLOBAL_SORT_IMP)

    self.assertEqual(len(self.GLOBAL_SORT_QUAL), len(actual_qual))
    self.assertEqual(len(self.GLOBAL_SORT_IMP), len(actual_imp))

    for k, actual in actual_qual.items():
      if k == tables.ASSESSED_CLASS:
        expected = '{{Assessed-Class}}'
      else:
        expected = '{{%s}}' % k.decode('utf-8')
      self.assertEqual(expected, actual)

    for k, actual in actual_imp.items():
      if k == tables.UNASSESSED_CLASS:
        expected = 'No-Class'
      else:
        expected = '{{%s}}' % k.decode('utf-8')
      self.assertEqual(expected, actual)

  def test_get_global_categories(self):
    actual = tables.get_global_categories()

    self.assertEqual(4, len(actual))
    self.assertTrue('sort_imp' in actual)
    self.assertTrue('sort_qual' in actual)
    self.assertTrue('qual_labels' in actual)
    self.assertTrue('imp_labels' in actual)

    self.assertEqual(self.GLOBAL_SORT_IMP, actual['sort_imp'])
    self.assertEqual(self.GLOBAL_SORT_QUAL, actual['sort_qual'])

class TablesDbTest(BaseWpOneDbTest):
  global_articles = [
    (225, 100, 475),
    (150, 0, 625),
    (100, 100, 229),
    (150, 100, 589),
    (150, 200, 596),
    (150, 100, 398),
    (0, 0, 109),
    (225, 100, 434),
    (150, 300, 629),
    (150, 300, 629),
    (150, 300, 629),
    (100, 100, 461),
    (225, 0, 288),
    (0, 0, 35),
    (150, 100, 665),
    (150, 100, 527),
    (100,0, 176),
    (150, 100, 37),
    (15, 100, 279),
    (150, 100, 279),
    (100, 100, 415),
  ]

  ratings = [
    (b'Art of testing', b'FA-Class', b'Top-Class'),
    (b'Testing mechanics', b'FA-Class', b'Top-Class'),
    (b'Rules of testing', b'FA-Class', b'Top-Class'),
    (b'Test practices', b'FL-Class', b'Top-Class'),
    (b'Testing history', b'FL-Class', b'High-Class'),
    (b'Test frameworks', b'FL-Class', b'High-Class'),
    (b'Testing figures', b'A-Class', b'High-Class'),
    (b'Important tests', b'A-Class', b'High-Class'),
    (b'Test results', b'A-Class', b'Mid-Class'),
    (b'Test main inheritance', b'GA-Class', b'Mid-Class'),
    (b'Test sub inheritance', b'GA-Class', b'Mid-Class'),
    (b'Test other inheritance', b'GA-Class', b'Mid-Class'),
    (b'Testing best practices', b'B-Class', b'Low-Class'),
    (b'Testing tools', b'B-Class', b'Low-Class'),
    (b'Operation of tests', b'B-Class', b'Low-Class'),
    (b'Lesser-known tests', b'C-Class', b'Low-Class'),
    (b'Failures of tests', b'C-Class', b'Low-Class'),
    (b'How to test', b'C-Class', b'Low-Class')
  ]

  def _insert_ratings(self):
    for r in self.ratings:
      rating = Rating(
        r_project=b'Test Project', r_namespace=0, r_article=r[0])
      rating.r_quality = r[1]
      rating.r_quality_timestamp = GLOBAL_TIMESTAMP_WIKI
      rating.r_importance = r[2]
      rating.r_importance_timestamp = GLOBAL_TIMESTAMP_WIKI

      with self.wp10db.cursor() as cursor:
        cursor.execute('INSERT INTO ' + Rating.table_name + '''
          (r_project, r_namespace, r_article, r_score, r_quality,
           r_quality_timestamp, r_importance, r_importance_timestamp)
          VALUES (%(r_project)s, %(r_namespace)s, %(r_article)s, %(r_score)s,
                  %(r_quality)s, %(r_quality_timestamp)s, %(r_importance)s,
                  %(r_importance_timestamp)s)
        ''', attr.asdict(rating))
      self.wp10db.commit()

  def _setup_global_articles(self):
    with self.wp10db.cursor() as cursor:
      for i, scores in enumerate(self.global_articles):
        cursor.execute('''
          INSERT INTO global_articles
            (a_article, a_quality, a_importance, a_score)
          VALUES (%s, %s, %s, %s)
        ''', ('Test Article %s' % i,) + scores)
    self.wp10db.commit()

  def _setup_project_categories(self):
    pass

  def setUp(self):
    super().setUp()
    self._setup_global_articles()
    self._insert_ratings()
    self._setup_project_categories()

  def test_get_global_stats(self):
    expected = [
      {'n': 2, 'q': b'C-Class', 'i': b'Low-Class'},
      {'n': 1, 'q': b'C-Class', 'i': b'Unknown-Class'},
      {'n': 3, 'q': b'Start-Class', 'i': b'High-Class'},
      {'n': 6, 'q': b'Start-Class', 'i': b'Low-Class'},
      {'n': 1, 'q': b'Start-Class', 'i': b'Mid-Class'},
      {'n': 1, 'q': b'Start-Class', 'i': b'Unknown-Class'},
      {'n': 3, 'q': b'Stub-Class', 'i': b'Low-Class'},
      {'n': 1, 'q': b'Stub-Class', 'i': b'Unknown-Class'},
      {'n': 2, 'q': b'Unassessed-Class', 'i': b'Unknown-Class'}
    ]
    actual = tables.get_global_stats(self.wp10db)
    self.assertEqual(expected, actual)

  def test_get_project_stats(self):
    expected = [
      {'n': 3, 'q': b'FA-Class', 'i': b'Top-Class', 'project': b'Test Project'},
      {'n': 3, 'q': b'C-Class', 'i': b'Low-Class', 'project': b'Test Project'},
      {'n': 2, 'q': b'A-Class', 'i': b'High-Class', 'project': b'Test Project'},
      {'n': 3, 'q': b'B-Class', 'i': b'Low-Class', 'project': b'Test Project'},
      {'n': 2, 'q': b'FL-Class', 'i': b'High-Class', 'project': b'Test Project'},
      {'n': 3, 'q': b'GA-Class', 'i': b'Mid-Class', 'project': b'Test Project'},
      {'n': 1, 'q': b'FL-Class', 'i': b'Top-Class', 'project': b'Test Project'},
      {'n': 1, 'q': b'A-Class', 'i': b'Mid-Class', 'project': b'Test Project'}
    ]
    actual = tables.get_project_stats(self.wp10db, 'Test Project')
    self.assertEqual(sorted(expected), sorted(actual))
