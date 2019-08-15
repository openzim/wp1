import unittest

import attr

from lucky import tables
from lucky.base_db_test import BaseWpOneDbTest
from lucky.constants import AssessmentKind, CATEGORY_NS_INT, GLOBAL_TIMESTAMP_WIKI, TS_FORMAT
from lucky.models.wp10.category import Category
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
    expected = [tuple(x.items()) for x in expected]
    actual = [tuple(x.items()) for x in actual]
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
    expected = [tuple(x.items()) for x in expected]
    actual = [tuple(x.items()) for x in actual]
    self.assertEqual(sorted(expected), sorted(actual))

  def test_db_project_categories(self):
    categories = [
      {'c_category': b'High-importance_Catholicism_articles',
       'c_ranking': 300,
       'c_rating': b'High-Class',
       'c_type': b'importance'},
       {'c_category': b'Low-importance_Catholicism_articles',
        'c_ranking': 100,
        'c_rating': b'Low-Class',
        'c_type': b'importance'},
       {'c_category': b'Mid-importance_Catholicism_articles',
        'c_ranking': 200,
        'c_rating': b'Mid-Class',
        'c_type': b'importance'},
       {'c_category': b'NA-importance_Catholicism_articles',
        'c_ranking': 25,
        'c_rating': b'NA-Class',
        'c_type': b'importance'},
       {'c_category': b'',
        'c_ranking': 21,
        'c_rating': b'NotA-Class',
        'c_type': b'importance'},
       {'c_category': b'Top-importance_Catholicism_articles',
        'c_ranking': 400,
        'c_rating': b'Top-Class',
        'c_type': b'importance'},
       {'c_category': b'Unknown-importance_Catholicism_articles',
        'c_ranking': 0,
        'c_rating': b'Unknown-Class',
        'c_type': b'importance'},
       {'c_category': b'A-Class_Catholicism_articles',
        'c_ranking': 425,
        'c_rating': b'A-Class',
        'c_type': b'quality'},
       {'c_category': b'B-Class_Catholicism_articles',
        'c_ranking': 300,
        'c_rating': b'B-Class',
        'c_type': b'quality'},
       {'c_category': b'Book-Class_Catholicism_articles',
        'c_ranking': 55,
        'c_rating': b'Book-Class',
        'c_type': b'quality'},
       {'c_category': b'C-Class_Catholicism_articles',
        'c_ranking': 225,
        'c_rating': b'C-Class',
        'c_type': b'quality'},
       {'c_category': b'Category-Class_Catholicism_articles',
        'c_ranking': 50,
        'c_rating': b'Category-Class',
        'c_type': b'quality'},
       {'c_category': b'Disambig-Class_Catholicism_articles',
        'c_ranking': 48,
        'c_rating': b'Disambig-Class',
        'c_type': b'quality'},
       {'c_category': b'FA-Class_Catholicism_articles',
        'c_ranking': 500,
        'c_rating': b'FA-Class',
        'c_type': b'quality'},
       {'c_category': b'FL-Class_Catholicism_articles',
        'c_ranking': 480,
        'c_rating': b'FL-Class',
        'c_type': b'quality'},
       {'c_category': b'FM-Class_Catholicism_articles',
        'c_ranking': 460,
        'c_rating': b'FM-Class',
        'c_type': b'quality'},
       {'c_category': b'File-Class_Catholicism_articles',
        'c_ranking': 46,
        'c_rating': b'File-Class',
        'c_type': b'quality'},
       {'c_category': b'GA-Class_Catholicism_articles',
        'c_ranking': 400,
        'c_rating': b'GA-Class',
        'c_type': b'quality'},
       {'c_category': b'Category:Image-Class Catholicism articles',
        'c_ranking': 47,
        'c_rating': b'Image-Class',
        'c_type': b'quality'},
       {'c_category': b'List-Class_Catholicism_articles',
        'c_ranking': 80,
        'c_rating': b'List-Class',
        'c_type': b'quality'},
       {'c_category': b'NA-Class_Catholicism_articles',
        'c_ranking': 25,
        'c_rating': b'NA-Class',
        'c_type': b'quality'},
       {'c_category': b'',
        'c_ranking': 21,
        'c_rating': b'NotA-Class',
        'c_type': b'quality'},
       {'c_category': b'Portal-Class_Catholicism_articles',
        'c_ranking': 45,
        'c_rating': b'Portal-Class',
        'c_type': b'quality'},
       {'c_category': b'Project-Class_Catholicism_articles',
        'c_ranking': 44,
        'c_rating': b'Project-Class',
        'c_type': b'quality'},
       {'c_category': b'Redirect-Class_Catholicism_articles',
        'c_ranking': 43,
        'c_rating': b'Redirect-Class',
        'c_type': b'quality'},
       {'c_category': b'Start-Class_Catholicism_articles',
        'c_ranking': 150,
        'c_rating': b'Start-Class',
        'c_type': b'quality'},
       {'c_category': b'Stub-Class_Catholicism_articles',
        'c_ranking': 100,
        'c_rating': b'Stub-Class',
        'c_type': b'quality'},
       {'c_category': b'Template-Class_Catholicism_articles',
        'c_ranking': 40,
        'c_rating': b'Template-Class',
        'c_type': b'quality'},
       {'c_category': b'Unassessed_Catholicism_articles',
        'c_ranking': 0,
        'c_rating': b'Unassessed-Class',
        'c_type': b'quality'},
    ]

    with self.wp10db.cursor() as cursor:
      cursor.executemany('INSERT INTO ' + Category.table_name + '''
          (c_project, c_type, c_rating, c_ranking, c_category, c_replacement)
        VALUES
          ('Catholicism', %(c_type)s, %(c_rating)s, %(c_ranking)s,
           %(c_category)s, %(c_rating)s)
      ''', categories)
    self.wp10db.commit()

    actual = tables.db_project_categories(self.wp10db, b'Catholicism')

    expected = sorted(categories, key=lambda x: x['c_ranking'])
    actual = sorted(actual, key=lambda x: x['c_ranking'])
    self.assertEqual(expected, actual)
