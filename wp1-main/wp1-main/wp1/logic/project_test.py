from datetime import datetime
from unittest.mock import patch, MagicMock
import time

import attr
import fakeredis

from wp1.base_db_test import BaseWpOneDbTest, BaseWikiDbTest, BaseCombinedDbTest
from wp1.conf import get_conf
from wp1.constants import AssessmentKind, CATEGORY_NS_INT, GLOBAL_TIMESTAMP_WIKI, TS_FORMAT
from wp1.logic import project as logic_project
from wp1.models.wiki.page import Page
from wp1.models.wp10.category import Category
from wp1.models.wp10.log import Log
from wp1.models.wp10.project import Project
from wp1.models.wp10.rating import Rating

config = get_conf()
QUALITY = config['QUALITY']
IMPORTANCE = config['IMPORTANCE']
NOT_A_CLASS = config['NOT_A_CLASS']
ROOT_CATEGORY = config['ROOT_CATEGORY']


def _get_first_category(wp10db):
  with wp10db.cursor() as cursor:
    cursor.execute('SELECT * FROM ' + Category.table_name +  # nosec
                   ' LIMIT 1')
    db_category = cursor.fetchone()
    return Category(**db_category) if db_category else None


def _get_all_categories(wp10db):
  with wp10db.cursor() as cursor:
    cursor.execute('SELECT * FROM ' + Category.table_name)  # nosec
    return [Category(**db_category) for db_category in cursor.fetchall()]


def _get_all_ratings(wp10db):
  with wp10db.cursor() as cursor:
    cursor.execute('SELECT * FROM ' + Rating.table_name)  # nosec
    return [Rating(**db_rating) for db_rating in cursor.fetchall()]


def _get_all_logs(wp10db):
  with wp10db.cursor() as cursor:
    cursor.execute('SELECT * FROM logging')
    return [Log(**db_log) for db_log in cursor.fetchall()]


def _get_all_global_article_scores(wp10db):
  with wp10db.cursor() as cursor:
    cursor.execute('SELECT * FROM global_articles')
    return cursor.fetchall()


class UpdateCategoryTest(BaseWpOneDbTest):

  def setUp(self):
    super().setUp()
    self.project = Project(p_project=b'Test Project', p_timestamp=None)
    self.page = Page(page_title=b'A-Class Test articles',
                     page_id=None,
                     page_namespace=None)
    self.page_1 = Page(page_title=b'Mid-importance Test articles',
                       page_id=None,
                       page_namespace=None)
    self.page_2 = Page(page_title=b'Draft-Class Test articles',
                       page_id=None,
                       page_namespace=None)

  def test_quality_gets_updated(self):
    rating_to_category = {}
    logic_project.update_category(self.wp10db, self.project, self.page, {},
                                  AssessmentKind.QUALITY, rating_to_category)

    category = _get_first_category(self.wp10db)
    self.assertEqual(self.page.page_title, rating_to_category['A-Class'][0])
    self.assertEqual(self.project.p_project, category.c_project)
    self.assertEqual(b'quality', category.c_type)
    self.assertEqual(b'A-Class', category.c_rating)
    self.assertEqual(self.page.page_title, category.c_category)
    self.assertEqual(QUALITY['A-Class'], category.c_ranking)
    self.assertEqual(b'A-Class', category.c_replacement)

  def test_importance_gets_updated(self):
    rating_to_category = {}
    logic_project.update_category(self.wp10db, self.project, self.page_1, {},
                                  AssessmentKind.IMPORTANCE, rating_to_category)

    category = _get_first_category(self.wp10db)
    self.assertEqual(self.page_1.page_title, rating_to_category['Mid-Class'][0])
    self.assertEqual(self.project.p_project, category.c_project)
    self.assertEqual(b'importance', category.c_type)
    self.assertEqual(b'Mid-Class', category.c_rating)
    self.assertEqual(self.page_1.page_title, category.c_category)
    self.assertEqual(IMPORTANCE['Mid-Class'], category.c_ranking)
    self.assertEqual(b'Mid-Class', category.c_replacement)

  def test_extra_category_gets_updated(self):
    rating_to_category = {}
    extra = {
        'extra': {
            self.page_2.page_title.decode('utf-8'): {
                'title': 'Draft-Class',
                'ranking': 10,
                'replaces': 'Disambig-Class',
            }
        }
    }
    logic_project.update_category(self.wp10db, self.project, self.page_2, extra,
                                  AssessmentKind.QUALITY, rating_to_category)

    category = _get_first_category(self.wp10db)
    self.assertEqual(self.page_2.page_title,
                     rating_to_category['Draft-Class'][0])
    self.assertEqual(self.project.p_project, category.c_project)
    self.assertEqual(b'quality', category.c_type)
    self.assertEqual(b'Draft-Class', category.c_rating)
    self.assertEqual(self.page_2.page_title, category.c_category)
    self.assertEqual(10, category.c_ranking)
    self.assertEqual(b'Disambig-Class', category.c_replacement)

  def test_extra_category_missing_title_no_update(self):
    rating_to_category = {}
    extra = {
        'extra': {
            self.page_2.page_title.decode('utf-8'): {
                'ranking': 10,
                'replaces': 'Disambig-Class',
            }
        }
    }
    logic_project.update_category(self.wp10db, self.project, self.page_2, extra,
                                  AssessmentKind.QUALITY, rating_to_category)

    category = _get_first_category(self.wp10db)
    self.assertIsNone(category)

  def test_extra_category_missing_ranking_no_update(self):
    rating_to_category = {}
    extra = {
        'extra': {
            self.page_2.page_title.decode('utf-8'): {
                'title': 'Draft-Class',
                'replaces': 'Disambig-Class',
            }
        }
    }
    logic_project.update_category(self.wp10db, self.project, self.page_2, extra,
                                  AssessmentKind.QUALITY, rating_to_category)

    category = _get_first_category(self.wp10db)
    self.assertIsNone(category)

  def test_extra_category_ranking_not_int_no_update(self):
    rating_to_category = {}
    extra = {
        'extra': {
            self.page_2.page_title.decode('utf-8'): {
                'title': 'Draft-Class',
                'ranking': '10b',
                'replaces': 'Disambig-Class',
            }
        }
    }
    logic_project.update_category(self.wp10db, self.project, self.page_2, extra,
                                  AssessmentKind.QUALITY, rating_to_category)

    category = _get_first_category(self.wp10db)
    self.assertIsNone(category)

  def test_skips_page_with_no_mapping_match(self):
    rating_to_category = {}
    page = Page(page_title=b'123*go', page_id=None, page_namespace=None)
    logic_project.update_category(self.wp10db, self.project, page, {},
                                  AssessmentKind.QUALITY, rating_to_category)

    category = _get_first_category(self.wp10db)
    self.assertIsNone(category)
    self.assertEqual(0, len(rating_to_category))

  def test_skips_page_with_no_class_match(self):
    rating_to_category = {}
    page = Page(page_title=b'Foo-Class Test articles',
                page_id=None,
                page_namespace=None)
    logic_project.update_category(self.wp10db, self.project, page, {},
                                  AssessmentKind.QUALITY, rating_to_category)

    category = _get_first_category(self.wp10db)
    self.assertIsNone(category)
    self.assertEqual(0, len(rating_to_category))


class UpdateProjectCategoriesByKindTest(BaseCombinedDbTest):
  quality_pages = (
      (101, b'FA-Class_Test_articles', b'Test_articles_by_quality', b'FA-Class',
       500),
      (102, b'FL-Class_Test_articles', b'Test_articles_by_quality', b'FL-Class',
       480),
      (103, b'A-Class_Test_articles', b'Test_articles_by_quality', b'A-Class',
       425),
      (104, b'GA-Class_Test_articles', b'Test_articles_by_quality', b'GA-Class',
       400),
      (105, b'B-Class_Test_articles', b'Test_articles_by_quality', b'B-Class',
       300),
      (106, b'C-Class_Test_articles', b'Test_articles_by_quality', b'C-Class',
       225),
  )

  additional_junk_pages = (
      (201, b'FA-Class_Foo_articles', b'Foo_articles_by_quality', b'FA-Class'),
      (202, b'FL-Class_Bar_articles', b'Bar_articles_by_quality', b'FL-Class'),
      (203, b'Mid-Class_Foo_articles', b'Foo_articles_by_importance',
       b'Mid-Class'),
      (204, b'Low-Class_Bar_articles', b'Bar_articles_by_importance',
       b'Low-Class'),
  )

  importance_pages = (
      (101, b'Top-Class_Test_articles', b'Test_articles_by_importance',
       b'Top-Class'),
      (102, b'High-Class_Test_articles', b'Test_articles_by_importance',
       b'High-Class'),
      (103, b'Mid-Class_Test_articles', b'Test_articles_by_importance',
       b'Mid-Class'),
      (104, b'Low-Class_Test_articles', b'Test_articles_by_importance',
       b'Low-Class'),
  )

  priority_pages = (
      (101, b'Top-Class_Test_articles', b'Test_articles_by_priority',
       b'Top-Class'),
      (102, b'High-Class_Test_articles', b'Test_articles_by_priority',
       b'High-Class'),
      (103, b'Mid-Class_Test_articles', b'Test_articles_by_priority',
       b'Mid-Class'),
      (104, b'Low-Class_Test_articles', b'Test_articles_by_priority',
       b'Low-Class'),
  )

  def _insert_pages(self, pages):
    with self.wikidb.cursor() as cursor:
      for p in pages:
        page_args = {'id': p[0], 'ns': 14, 'title': p[1]}
        cl_args = {'from': p[0], 'to': p[2]}
        cursor.execute(
            '''
            INSERT INTO page
              (page_id, page_namespace, page_title)
            VALUES
              (%(id)s, %(ns)s, %(title)s)
        ''', page_args)
        cursor.execute(
            '''
            INSERT INTO categorylinks
              (cl_from, cl_to)
            VALUES
              (%(from)s, %(to)s)
        ''', cl_args)

  def setUp(self):
    super().setUp()
    self.project = Project(p_project=b'Test', p_timestamp=None)
    self._insert_pages(self.additional_junk_pages)

  def test_update_quality(self):
    self._insert_pages(self.quality_pages)
    logic_project.update_project_categories_by_kind(self.wikidb, self.wp10db,
                                                    self.project, {},
                                                    AssessmentKind.QUALITY)

    categories = _get_all_categories(self.wp10db)
    self.assertNotEqual(0, len(categories))
    categories = [
        cat for cat in categories if cat.c_rating != NOT_A_CLASS.encode('utf-8')
    ]
    for category in categories:
      self.assertEqual(self.project.p_project, category.c_project)
      self.assertEqual(b'quality', category.c_type)

    category_titles = set(category.c_category for category in categories)
    expected_titles = set(p[1] for p in self.quality_pages)
    self.assertEqual(expected_titles, category_titles)

    category_ratings = set(category.c_rating for category in categories)
    expected_ratings = set(p[3] for p in self.quality_pages)
    self.assertEqual(expected_ratings, category_ratings)

    category_replaces = set(category.c_replacement for category in categories)
    self.assertEqual(expected_ratings, category_replaces)

  def test_update_quality_rating_to_category(self):
    self._insert_pages(self.quality_pages)
    rating_to_category = logic_project.update_project_categories_by_kind(
        self.wikidb, self.wp10db, self.project, {}, AssessmentKind.QUALITY)

    expected = dict(
        (p[3].decode('utf-8'), (p[1], p[4])) for p in self.quality_pages)
    self.assertEqual(expected, rating_to_category)

  def test_update_importance(self):
    self._insert_pages(self.importance_pages)
    logic_project.update_project_categories_by_kind(self.wikidb, self.wp10db,
                                                    self.project, {},
                                                    AssessmentKind.IMPORTANCE)

    categories = _get_all_categories(self.wp10db)
    self.assertNotEqual(0, len(categories))
    categories = [
        cat for cat in categories if cat.c_rating != NOT_A_CLASS.encode('utf-8')
    ]
    for category in categories:
      self.assertEqual(self.project.p_project, category.c_project)
      self.assertEqual(b'importance', category.c_type)

    category_titles = set(category.c_category for category in categories)
    expected_titles = set(p[1] for p in self.importance_pages)
    self.assertEqual(expected_titles, category_titles)

    category_ratings = set(category.c_rating for category in categories)
    expected_ratings = set(p[3] for p in self.importance_pages)
    self.assertEqual(expected_ratings, category_ratings)

    category_replaces = set(category.c_replacement for category in categories)
    self.assertEqual(expected_ratings, category_replaces)

  def test_update_priority(self):
    self._insert_pages(self.priority_pages)
    logic_project.update_project_categories_by_kind(self.wikidb, self.wp10db,
                                                    self.project, {},
                                                    AssessmentKind.IMPORTANCE)

    categories = _get_all_categories(self.wp10db)
    self.assertNotEqual(0, len(categories))
    categories = [
        cat for cat in categories if cat.c_rating != NOT_A_CLASS.encode('utf-8')
    ]
    for category in categories:
      self.assertEqual(self.project.p_project, category.c_project)
      self.assertEqual(b'importance', category.c_type)

    category_titles = set(category.c_category for category in categories)
    expected_titles = set(p[1] for p in self.priority_pages)
    self.assertEqual(expected_titles, category_titles)

    category_ratings = set(category.c_rating for category in categories)
    expected_ratings = set(p[3] for p in self.priority_pages)
    self.assertEqual(expected_ratings, category_ratings)

    category_replaces = set(category.c_replacement for category in categories)
    self.assertEqual(expected_ratings, category_replaces)


class ArticlesTest(BaseCombinedDbTest):
  old_ts_wiki = b'2018-07-04T05:05:05Z'
  expected_ts_wiki = b'2018-12-25T11:22:33Z'

  global_article_scores = [
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
      (100, 0, 176),
      (150, 100, 37),
      (15, 100, 279),
      (150, 100, 279),
      (100, 100, 415),
  ]

  custom_quality_pages = (
      (107, b'Draft-Class_Test_articles', b'Test_articles_by_quality', None,
       14),
      (270, b'Starting out testing', b'Draft-Class_Test_articles',
       b'Draft-Class', 1),
      (271, b'Your First Test', b'Draft-Class_Test_articles', b'Draft-Class',
       1),
  )

  quality_pages = (
      (101, b'FA-Class_Test_articles', b'Test_articles_by_quality', None, 14),
      (102, b'FL-Class_Test_articles', b'Test_articles_by_quality', None, 14),
      (103, b'GA-Class_Test_articles', b'Test_articles_by_quality', None, 14),
      (104, b'A-Class_Test_articles', b'Test_articles_by_quality', None, 14),
      (105, b'B-Class_Test_articles', b'Test_articles_by_quality', None, 14),
      (106, b'C-Class_Test_articles', b'Test_articles_by_quality', None, 14),
      (201, b'Art of testing', b'FA-Class_Test_articles', b'FA-Class', 1),
      (202, b'Testing mechanics', b'FA-Class_Test_articles', b'FA-Class', 1),
      (203, b'Rules of testing', b'FA-Class_Test_articles', b'FA-Class', 1),
      (210, b'Test practices', b'FL-Class_Test_articles', b'FL-Class', 1),
      (211, b'Testing history', b'FL-Class_Test_articles', b'FL-Class', 1),
      (212, b'Test frameworks', b'FL-Class_Test_articles', b'FL-Class', 1),
      (220, b'Testing figures', b'A-Class_Test_articles', b'A-Class', 1),
      (221, b'Important tests', b'A-Class_Test_articles', b'A-Class', 1),
      (222, b'Test results', b'A-Class_Test_articles', b'A-Class', 1),
      (230, b'Test main inheritance', b'GA-Class_Test_articles', b'GA-Class',
       1),
      (231, b'Test sub inheritance', b'GA-Class_Test_articles', b'GA-Class', 1),
      (232, b'Test other inheritance', b'GA-Class_Test_articles', b'GA-Class',
       1),
      (240, b'Testing best practices', b'B-Class_Test_articles', b'B-Class', 1),
      (241, b'Testing tools', b'B-Class_Test_articles', b'B-Class', 1),
      (242, b'Operation of tests', b'B-Class_Test_articles', b'B-Class', 1),
      (250, b'Lesser-known tests', b'C-Class_Test_articles', b'C-Class', 1),
      (251, b'Failures of tests', b'C-Class_Test_articles', b'C-Class', 1),
      (252, b'How to test', b'C-Class_Test_articles', b'C-Class', 1),
  )

  multiple_quality_pages = (
      (260, b'Lesser-known tests', b'A-Class_Test_articles', b'A-Class', 1),
      (261, b'Failures of tests', b'A-Class_Test_articles', b'A-Class', 1),
      (262, b'How to test', b'A-Class_Test_articles', b'A-Class', 1),
  )

  importance_pages = (
      (1010, b'Top-Class_Test_articles', b'Test_articles_by_importance', None,
       14),
      (1020, b'High-Class_Test_articles', b'Test_articles_by_importance', None,
       14),
      (1030, b'Mid-Class_Test_articles', b'Test_articles_by_importance', None,
       14),
      (1040, b'Low-Class_Test_articles', b'Test_articles_by_importance', None,
       14),
      (2010, b'Art of testing', b'Top-Class_Test_articles', b'Top-Class', 1),
      (2020, b'Testing mechanics', b'Top-Class_Test_articles', b'Top-Class', 1),
      (2030, b'Rules of testing', b'Top-Class_Test_articles', b'Top-Class', 1),
      (2040, b'Test practices', b'Top-Class_Test_articles', b'Top-Class', 1),
      (2110, b'Testing history', b'High-Class_Test_articles', b'High-Class', 1),
      (2120, b'Test frameworks', b'High-Class_Test_articles', b'High-Class', 1),
      (2200, b'Testing figures', b'High-Class_Test_articles', b'High-Class', 1),
      (2210, b'Important tests', b'High-Class_Test_articles', b'High-Class', 1),
      (2220, b'Test results', b'Mid-Class_Test_articles', b'Mid-Class', 1),
      (2300, b'Test main inheritance', b'Mid-Class_Test_articles', b'Mid-Class',
       1),
      (2310, b'Test sub inheritance', b'Mid-Class_Test_articles', b'Mid-Class',
       1),
      (2320, b'Test other inheritance', b'Mid-Class_Test_articles',
       b'Mid-Class', 1),
      (2400, b'Testing best practices', b'Low-Class_Test_articles',
       b'Low-Class', 1),
      (2410, b'Testing tools', b'Low-Class_Test_articles', b'Low-Class', 1),
      (2420, b'Operation of tests', b'Low-Class_Test_articles', b'Low-Class',
       1),
      (2500, b'Lesser-known tests', b'Low-Class_Test_articles', b'Low-Class',
       1),
      (2510, b'Failures of tests', b'Low-Class_Test_articles', b'Low-Class', 1),
      (2520, b'How to test', b'Low-Class_Test_articles', b'Low-Class', 1),
  )

  multiple_importance_pages = (
      (2620, b'Operation of tests', b'Mid-Class_Test_articles', b'Mid-Class',
       1),
      (2600, b'Lesser-known tests', b'Mid-Class_Test_articles', b'Mid-Class',
       1),
      (2710, b'Failures of tests', b'Mid-Class_Test_articles', b'Mid-Class', 1),
      (2720, b'How to test', b'Mid-Class_Test_articles', b'Mid-Class', 1),
  )

  def _insert_pages(self, pages):
    ts = datetime(2018, 12, 25, 11, 22, 33)
    with self.wikidb.cursor() as cursor:
      for p in pages:
        page_args = {'id': p[0], 'ns': p[4], 'title': p[1]}
        cl_args = {'from': p[0], 'to': p[2], 'ts': ts}
        cursor.execute('SELECT * FROM page WHERE page_id = %s', (p[0],))
        if cursor.fetchone() is None:
          cursor.execute(
              '''
              INSERT INTO page
                (page_id, page_namespace, page_title)
              VALUES
                (%(id)s, %(ns)s, %(title)s)
          ''', page_args)

        cursor.execute(
            '''
            INSERT INTO categorylinks
              (cl_from, cl_to, cl_timestamp)
            VALUES
              (%(from)s, %(to)s, %(ts)s)
        ''', cl_args)
    self.wikidb.commit()

  def _insert_ratings(self, pages, namespace, kind, override_rating=None):
    for p in pages:
      if kind == 'both' and override_rating is None:
        r = (p[0][3], p[1][3])
        art = p[0][1]
      else:
        r = p[3]
        art = p[1]
      if override_rating is not None:
        r = override_rating
      rating = Rating(r_project=self.project.p_project,
                      r_namespace=namespace,
                      r_article=art)
      if kind == AssessmentKind.QUALITY or kind == 'both':
        if isinstance(r, tuple):
          rating.r_quality = r[0]
        else:
          rating.r_quality = r
        rating.r_quality_timestamp = self.old_ts_wiki
      elif kind == AssessmentKind.IMPORTANCE or kind == 'both':
        if isinstance(r, tuple):
          rating.r_importance = r[1]
        else:
          rating.r_importance = r
        rating.r_importance_timestamp = self.old_ts_wiki

      with self.wp10db.cursor() as cursor:
        cursor.execute(
            '''
            INSERT INTO ratings
              (r_project, r_namespace, r_article, r_score, r_quality,
               r_quality_timestamp, r_importance, r_importance_timestamp)
            VALUES
              (%(r_project)s, %(r_namespace)s, %(r_article)s, %(r_score)s,
               %(r_quality)s, %(r_quality_timestamp)s, %(r_importance)s,
               %(r_importance_timestamp)s)
        ''', attr.asdict(rating))
    self.wp10db.commit()

  def _insert_global_scores(self):
    article_scores = [(art[1],) + score for score, art in zip(
        self.global_article_scores, self.quality_pages[6:])]
    with self.wp10db.cursor() as cursor:
      cursor.executemany(
          '''
          INSERT INTO global_articles
            (a_article, a_quality, a_importance, a_score)
          VALUES (%s, %s, %s, %s)
      ''', article_scores)
    self.wp10db.commit()

  def setUp(self):
    super().setUp()
    self.project = Project(p_project=b'Test', p_timestamp=b'20100101000000')


class UpdateProjectAssessmentsTest(ArticlesTest):

  def setUp(self):
    super().setUp()

    self.timestamp_str = '2011-04-28T12:30:00Z'
    self.expected_ns = 0
    self.expected_title = 'Test Moving'
    self.expected_dt = datetime.strptime(self.timestamp_str, TS_FORMAT)

    self.api_return = {
        'query': {
            'redirects': [{
                'to': self.expected_title
            }],
            'pages': {
                123: {
                    'ns': self.expected_ns,
                    'title': self.expected_title,
                    'revisions': [{
                        'timestamp': self.timestamp_str
                    }],
                }
            },
        },
    }

  def test_old_rating_same_quality(self):
    self._insert_pages(self.quality_pages)
    self._insert_ratings(self.quality_pages[6:], 0, AssessmentKind.QUALITY)

    logic_project.update_project_assessments(self.wikidb, self.wp10db,
                                             self.project, {})

    ratings = _get_all_ratings(self.wp10db)
    self.assertNotEqual(0, len(ratings))

    pages = self.quality_pages[6:]
    expected_titles = set(p[1] for p in pages)
    actual_titles = set(r.r_article for r in ratings)
    self.assertEqual(expected_titles, actual_titles)

    page_to_rating = dict((p[1], p[3]) for p in pages)
    for r in ratings:
      self.assertEqual(page_to_rating[r.r_article], r.r_quality)

  def test_old_rating_same_importance(self):
    self._insert_pages(self.importance_pages)
    self._insert_ratings(self.importance_pages[4:], 0,
                         AssessmentKind.IMPORTANCE)

    logic_project.update_project_assessments(self.wikidb, self.wp10db,
                                             self.project, {})

    ratings = _get_all_ratings(self.wp10db)
    self.assertNotEqual(0, len(ratings))

    pages = self.importance_pages[4:]
    expected_titles = set(p[1] for p in pages)
    actual_titles = set(r.r_article for r in ratings)
    self.assertEqual(expected_titles, actual_titles)

    page_to_rating = dict((p[1], p[3]) for p in pages)
    for r in ratings:
      self.assertEqual(page_to_rating[r.r_article], r.r_importance)

  def test_old_rating_update_quality(self):
    self._insert_pages(self.quality_pages)
    self._insert_ratings(self.quality_pages[6:],
                         0,
                         AssessmentKind.QUALITY,
                         override_rating=NOT_A_CLASS.encode('utf-8'))

    logic_project.update_project_assessments(self.wikidb, self.wp10db,
                                             self.project, {})

    ratings = _get_all_ratings(self.wp10db)
    self.assertNotEqual(0, len(ratings))

    pages = self.quality_pages[6:]
    expected_titles = set(p[1] for p in pages)
    actual_titles = set(r.r_article for r in ratings)
    self.assertEqual(expected_titles, actual_titles)

    page_to_rating = dict((p[1], p[3]) for p in pages)
    for r in ratings:
      self.assertEqual(page_to_rating[r.r_article], r.r_quality, r)

  def test_old_rating_update_importance(self):
    self._insert_pages(self.importance_pages)
    self._insert_ratings(self.importance_pages[4:],
                         0,
                         AssessmentKind.IMPORTANCE,
                         override_rating=NOT_A_CLASS.encode('utf-8'))

    logic_project.update_project_assessments(self.wikidb, self.wp10db,
                                             self.project, {})

    ratings = _get_all_ratings(self.wp10db)
    self.assertNotEqual(0, len(ratings))

    pages = self.importance_pages[4:]
    expected_titles = set(p[1] for p in pages)
    actual_titles = set(r.r_article for r in ratings)
    self.assertEqual(expected_titles, actual_titles)

    page_to_rating = dict((p[1], p[3]) for p in pages)
    for r in ratings:
      self.assertEqual(page_to_rating[r.r_article], r.r_importance)

  def test_old_rating_update_both(self):
    self._insert_pages(self.quality_pages)
    self._insert_pages(self.importance_pages)
    self._insert_ratings(self.quality_pages[6:],
                         0,
                         'both',
                         override_rating=NOT_A_CLASS.encode('utf-8'))

    logic_project.update_project_assessments(self.wikidb, self.wp10db,
                                             self.project, {})

    ratings = _get_all_ratings(self.wp10db)
    self.assertNotEqual(0, len(ratings))

    q_pages = self.quality_pages[6:]
    i_pages = self.importance_pages[4:]
    expected_titles = set(p[1] for p in q_pages)
    actual_titles = set(r.r_article for r in ratings)
    self.assertEqual(expected_titles, actual_titles)

    q_page_to_rating = dict((p[1], p[3]) for p in q_pages)
    i_page_to_rating = dict((p[1], p[3]) for p in i_pages)
    for r in ratings:
      self.assertEqual(q_page_to_rating[r.r_article], r.r_quality)
      self.assertEqual(i_page_to_rating[r.r_article], r.r_importance)

  def test_new_rating_quality(self):
    self._insert_pages(self.quality_pages)

    expected_global_ts = b'20190113000000'
    with patch('wp1.logic.rating.GLOBAL_TIMESTAMP', expected_global_ts):
      logic_project.update_project_assessments(self.wikidb, self.wp10db,
                                               self.project, {})

    ratings = _get_all_ratings(self.wp10db)
    self.assertNotEqual(0, len(ratings))

    q_pages = self.quality_pages[6:]
    expected_titles = set(p[1] for p in q_pages)
    actual_titles = set(r.r_article for r in ratings)
    self.assertEqual(expected_titles, actual_titles)

    q_page_to_rating = dict((p[1], p[3]) for p in q_pages)
    for r in ratings:
      self.assertEqual(q_page_to_rating[r.r_article], r.r_quality)

    logs = _get_all_logs(self.wp10db)
    self.assertEqual(len(q_pages), len(logs))

    actual_log_titles = set(l.l_article for l in logs)
    self.assertEqual(expected_titles, actual_log_titles)

    for l in logs:
      self.assertEqual(NOT_A_CLASS.encode('utf-8'), l.l_old)
      self.assertEqual(q_page_to_rating[l.l_article], l.l_new)
      self.assertEqual(b'Test', l.l_project)
      self.assertEqual(0, l.l_namespace)
      self.assertEqual(self.expected_ts_wiki, l.l_revision_timestamp)
      self.assertEqual(expected_global_ts, l.l_timestamp)

  def test_new_rating_importance(self):
    self._insert_pages(self.importance_pages)

    expected_global_ts = b'20190113000000'
    with patch('wp1.logic.rating.GLOBAL_TIMESTAMP', expected_global_ts):
      logic_project.update_project_assessments(self.wikidb, self.wp10db,
                                               self.project, {})

    ratings = _get_all_ratings(self.wp10db)
    self.assertNotEqual(0, len(ratings))

    i_pages = self.importance_pages[4:]
    expected_titles = set(p[1] for p in i_pages)
    actual_titles = set(r.r_article for r in ratings)
    self.assertEqual(expected_titles, actual_titles)

    i_page_to_rating = dict((p[1], p[3]) for p in i_pages)
    for r in ratings:
      self.assertEqual(i_page_to_rating[r.r_article], r.r_importance)

    logs = _get_all_logs(self.wp10db)
    self.assertEqual(len(i_pages), len(logs))

    actual_log_titles = set(l.l_article for l in logs)
    self.assertEqual(expected_titles, actual_log_titles)

    for l in logs:
      self.assertEqual(NOT_A_CLASS.encode('utf-8'), l.l_old)
      self.assertEqual(i_page_to_rating[l.l_article], l.l_new)
      self.assertEqual(b'Test', l.l_project)
      self.assertEqual(0, l.l_namespace)
      self.assertEqual(self.expected_ts_wiki, l.l_revision_timestamp)
      self.assertEqual(expected_global_ts, l.l_timestamp)

  def test_new_rating_both(self):
    self._insert_pages(self.importance_pages)
    self._insert_pages(self.quality_pages)

    expected_global_ts = b'20190113000000'
    with patch('wp1.logic.rating.GLOBAL_TIMESTAMP', expected_global_ts):
      logic_project.update_project_assessments(self.wikidb, self.wp10db,
                                               self.project, {})

    ratings = _get_all_ratings(self.wp10db)
    self.assertNotEqual(0, len(ratings))

    q_pages = self.quality_pages[6:]
    i_pages = self.importance_pages[4:]
    expected_q_titles = set(p[1] for p in q_pages)
    expected_i_titles = set(p[1] for p in i_pages)
    self.assertEqual(expected_q_titles, expected_i_titles)
    actual_titles = set(r.r_article for r in ratings)
    self.assertEqual(expected_q_titles, actual_titles)

    q_page_to_rating = dict((p[1], p[3]) for p in q_pages)
    for r in ratings:
      self.assertEqual(q_page_to_rating[r.r_article], r.r_quality)

    i_page_to_rating = dict((p[1], p[3]) for p in i_pages)
    for r in ratings:
      self.assertEqual(i_page_to_rating[r.r_article], r.r_importance)

    logs = _get_all_logs(self.wp10db)
    self.assertEqual(len(q_pages) + len(i_pages), len(logs))

  def test_custom_rating(self):
    self._insert_pages(self.quality_pages)
    self._insert_pages(self.custom_quality_pages)

    extra = {
        'extra': {
            'Draft-Class_Test_articles': {
                'category': 'Draft-Class_Test_articles',
                'ranking': '10',
                'title': 'Draft-Class',
                'type': 'quality'
            }
        }
    }

    expected_global_ts = b'20190113000000'
    with patch('wp1.logic.rating.GLOBAL_TIMESTAMP', expected_global_ts):
      logic_project.update_project_assessments(self.wikidb, self.wp10db,
                                               self.project, extra)

    ratings = _get_all_ratings(self.wp10db)
    self.assertNotEqual(0, len(ratings))

    q_pages = self.custom_quality_pages[1:]
    expected_titles = set(p[1] for p in q_pages)
    actual_titles = set(r.r_article for r in ratings)
    for title in expected_titles:
      self.assertTrue(title in actual_titles,
                      '%s not in %s' % (title, actual_titles))

    q_page_to_rating = dict((p[1], p[3]) for p in q_pages)
    for r in ratings:
      if r.r_article in q_page_to_rating:
        self.assertEqual(q_page_to_rating[r.r_article], r.r_quality)

  def _do_assessment(self):
    expected_global_ts = b'20190113000000'
    with patch('wp1.logic.rating.GLOBAL_TIMESTAMP', expected_global_ts):
      logic_project.update_project_assessments(self.wikidb, self.wp10db,
                                               self.project, {})

  def _assert_updated_quality_ratings(self, assert_log_len=True):
    ratings = _get_all_ratings(self.wp10db)
    self.assertNotEqual(0, len(ratings))

    q_pages = self.quality_pages[6:]
    expected_titles = set(p[1] for p in q_pages)
    actual_titles = set(r.r_article for r in ratings)
    self.assertEqual(expected_titles, actual_titles)

    q_page_to_rating = dict((p[1], p[3]) for p in q_pages)
    q_page_to_rating.update(
        dict((p[1], p[3]) for p in self.multiple_quality_pages))
    for r in ratings:
      self.assertEqual(q_page_to_rating[r.r_article], r.r_quality)

    if assert_log_len:
      logs = _get_all_logs(self.wp10db)
      self.assertEqual(len(q_pages), len(logs))

  def _assert_updated_importance_ratings(self, assert_log_len=True):
    ratings = _get_all_ratings(self.wp10db)
    self.assertNotEqual(0, len(ratings))

    i_pages = self.importance_pages[4:]
    expected_titles = set(p[1] for p in i_pages)
    actual_titles = set(r.r_article for r in ratings)
    self.assertEqual(expected_titles, actual_titles)

    i_page_to_rating = dict((p[1], p[3]) for p in i_pages)
    i_page_to_rating.update(
        dict((p[1], p[3]) for p in self.multiple_importance_pages))
    for r in ratings:
      self.assertEqual(i_page_to_rating[r.r_article], r.r_importance)

    if assert_log_len:
      logs = _get_all_logs(self.wp10db)
      self.assertEqual(len(i_pages), len(logs))

  def test_multiple_new_quality(self):
    self._insert_pages(self.quality_pages)
    self._insert_pages(self.multiple_quality_pages)

    self._do_assessment()
    self._assert_updated_quality_ratings()

  def test_multiple_existing_quality(self):
    self._insert_pages(self.quality_pages)
    self._insert_pages(self.multiple_quality_pages)
    self._insert_ratings(self.multiple_quality_pages, 0, AssessmentKind.QUALITY)

    self._do_assessment()
    self._assert_updated_quality_ratings(assert_log_len=False)

  def test_multiple_new_importance(self):
    self._insert_pages(self.importance_pages)
    self._insert_pages(self.multiple_importance_pages)

    self._do_assessment()
    self._assert_updated_importance_ratings()

  def test_multiple_existing_importance(self):
    self._insert_pages(self.importance_pages)
    self._insert_pages(self.multiple_importance_pages)
    self._insert_ratings(self.multiple_importance_pages, 0,
                         AssessmentKind.IMPORTANCE)

    self._do_assessment()
    self._assert_updated_importance_ratings(assert_log_len=False)

  def test_multiple_new_both(self):
    self._insert_pages(self.importance_pages)
    self._insert_pages(self.multiple_importance_pages)
    self._insert_pages(self.quality_pages)
    self._insert_pages(self.multiple_quality_pages)

    self._do_assessment()
    self._assert_updated_quality_ratings(assert_log_len=False)
    self._assert_updated_importance_ratings(assert_log_len=False)

  @patch('wp1.logic.api.page.site')
  def test_not_seen_quality(self, patched_site):
    self._insert_pages(self.quality_pages[:-2])
    self._insert_ratings(self.quality_pages[6:], 0, AssessmentKind.QUALITY)

    def fake_api(*args, **kwargs):
      if kwargs['titles'] == ':How to test':
        return self.api_return
      return {}

    patched_site.api.side_effect = fake_api

    logic_project.update_project_assessments(self.wikidb, self.wp10db,
                                             self.project, {})

    self.assertEqual(2, len(patched_site.api.call_args_list))

    ratings = _get_all_ratings(self.wp10db)
    self.assertNotEqual(0, len(ratings))

    pages = self.quality_pages[6:]
    expected_titles = set(p[1] for p in pages)
    actual_titles = set(r.r_article for r in ratings)
    self.assertEqual(expected_titles, actual_titles)

    page_to_rating = dict((p[1], p[3]) for p in pages)
    for r in ratings:
      if r.r_article in (b'How to test', b'Failures of tests'):
        self.assertIsNone(r.r_quality)
      else:
        self.assertEqual(page_to_rating[r.r_article], r.r_quality)

  @patch('wp1.logic.api.page.site')
  def test_not_seen_importance(self, patched_site):
    self._insert_pages(self.importance_pages[:-2])
    self._insert_ratings(self.importance_pages[4:], 0,
                         AssessmentKind.IMPORTANCE)

    def fake_api(*args, **kwargs):
      if kwargs['titles'] == ':How to test':
        return self.api_return
      return {}

    patched_site.api.side_effect = fake_api

    logic_project.update_project_assessments(self.wikidb, self.wp10db,
                                             self.project, {})

    self.assertEqual(2, len(patched_site.api.call_args_list))

    ratings = _get_all_ratings(self.wp10db)
    self.assertNotEqual(0, len(ratings))

    pages = self.importance_pages[4:]
    expected_titles = set(p[1] for p in pages)
    actual_titles = set(r.r_article for r in ratings)
    self.assertEqual(expected_titles, actual_titles)

    page_to_rating = dict((p[1], p[3]) for p in pages)
    for r in ratings:
      if r.r_article in (b'How to test', b'Failures of tests'):
        self.assertIsNone(r.r_quality)
      else:
        self.assertEqual(page_to_rating[r.r_article], r.r_importance, repr(r))

  @patch('wp1.logic.api.page.site')
  def test_not_seen_null_quality(self, patched_site):
    self._insert_pages(self.quality_pages)
    self._insert_ratings(self.quality_pages[6:],
                         0,
                         AssessmentKind.QUALITY,
                         override_rating=None)

    def fake_api(*args, **kwargs):
      if kwargs['titles'] == ':How to test':
        return self.api_return
      return {}

    patched_site.api.side_effect = fake_api

    logic_project.update_project_assessments(self.wikidb, self.wp10db,
                                             self.project, {})

    patched_site.assert_not_called()

  @patch('wp1.logic.api.page.site')
  def test_not_seen_null_importance(self, patched_site):
    self._insert_pages(self.importance_pages)
    self._insert_ratings(self.importance_pages[6:],
                         0,
                         AssessmentKind.IMPORTANCE,
                         override_rating=None)

    def fake_api(*args, **kwargs):
      if kwargs['titles'] == ':How to test':
        return self.api_return
      return {}

    patched_site.api.side_effect = fake_api

    logic_project.update_project_assessments(self.wikidb, self.wp10db,
                                             self.project, {})

    patched_site.assert_not_called()


class GlobalArticlesTest(ArticlesTest):

  def setUp(self):
    super().setUp()
    self._insert_pages(self.quality_pages)
    self._insert_pages(self.importance_pages)
    self._insert_ratings(zip(self.quality_pages[6:], self.importance_pages[4:]),
                         0, 'both')

    self._insert_global_scores()

  @patch('wp1.logic.project.api_project.get_extra_assessments', return_value={'extra': {}})
  def test_update_global_articles_table(self, mock_api_project):
    expected = [{
        'a_article': b'Art of testing',
        'a_importance': b'400',
        'a_quality': b'500',
        'a_score': 475
    }, {
        'a_article': b'Failures of tests',
        'a_importance': b'100',
        'a_quality': b'225',
        'a_score': 176
    }, {
        'a_article': b'How to test',
        'a_importance': b'100',
        'a_quality': b'225',
        'a_score': 37
    }, {
        'a_article': b'Important tests',
        'a_importance': b'300',
        'a_quality': b'425',
        'a_score': 434
    }, {
        'a_article': b'Lesser-known tests',
        'a_importance': b'100',
        'a_quality': b'225',
        'a_score': 527
    }, {
        'a_article': b'Operation of tests',
        'a_importance': b'100',
        'a_quality': b'300',
        'a_score': 665
    }, {
        'a_article': b'Rules of testing',
        'a_importance': b'400',
        'a_quality': b'500',
        'a_score': 229
    }, {
        'a_article': b'Test frameworks',
        'a_importance': b'300',
        'a_quality': b'480',
        'a_score': 398
    }, {
        'a_article': b'Test main inheritance',
        'a_importance': b'300',
        'a_quality': b'400',
        'a_score': 629
    }, {
        'a_article': b'Test other inheritance',
        'a_importance': b'200',
        'a_quality': b'400',
        'a_score': 461
    }, {
        'a_article': b'Test practices',
        'a_importance': b'400',
        'a_quality': b'480',
        'a_score': 589
    }, {
        'a_article': b'Test results',
        'a_importance': b'300',
        'a_quality': b'425',
        'a_score': 629
    }, {
        'a_article': b'Test sub inheritance',
        'a_importance': b'300',
        'a_quality': b'400',
        'a_score': 629
    }, {
        'a_article': b'Testing best practices',
        'a_importance': b'100',
        'a_quality': b'300',
        'a_score': 288
    }, {
        'a_article': b'Testing figures',
        'a_importance': b'300',
        'a_quality': b'425',
        'a_score': 109
    }, {
        'a_article': b'Testing history',
        'a_importance': b'300',
        'a_quality': b'480',
        'a_score': 596
    }, {
        'a_article': b'Testing mechanics',
        'a_importance': b'400',
        'a_quality': b'500',
        'a_score': 625
    }, {
        'a_article': b'Testing tools',
        'a_importance': b'100',
        'a_quality': b'300',
        'a_score': 35
    }]

    logic_project.update_project(self.wikidb, self.wp10db, self.project)
    logic_project.update_global_articles_for_project_name(
        self.wp10db, self.project.p_project)

    actual = _get_all_global_article_scores(self.wp10db)
    actual = sorted(sorted(list(a.items())) for a in actual)
    expected = sorted(sorted(list(e.items())) for e in expected)
    self.assertEqual(expected, actual)


class CleanupProjectTest(BaseWpOneDbTest):
  ratings = (
      (b'Art of testing', b'FA-Class', b'High-Class'),
      (b'Testing mechanics', b'FA-Class', b'Mid-Class'),
      (b'Rules of testing', b'FA-Class', b'NotA-Class'),
      (b'Test frameworks', b'NotA-Class', b'Mid-Class'),
      (b'Test practices', b'FL-Class', None),
      (b'Testing history', b'FL-Class', None),
      (b'Testing figures', None, b'Low-Class'),
      (b'Important tests', None, b'Low-Class'),
      (b'Test results', b'NotA-Class', b'NotA-Class'),
      (b'Test main inheritance', b'NotA-Class', b'NotA-Class'),
      (b'Failures of tests', None, None),
      (b'How to test', None, None),
  )
  not_a_class_db = NOT_A_CLASS.encode('utf-8')

  def setUp(self):
    super().setUp()
    self.project = Project(p_project=b'Test', p_timestamp=None)

    qual_ts = b'2018-04-01T12:30:00Z'
    imp_ts = b'2018-05-01T13:45:10Z'
    with self.wp10db.cursor() as cursor:
      for r in self.ratings:
        rating = Rating(r_project=self.project.p_project,
                        r_namespace=0,
                        r_article=r[0],
                        r_quality=r[1],
                        r_importance=r[2],
                        r_quality_timestamp=qual_ts,
                        r_importance_timestamp=imp_ts)
        cursor.execute(
            '''
            INSERT INTO ratings
              (r_project, r_namespace, r_article, r_score, r_quality,
               r_quality_timestamp, r_importance, r_importance_timestamp)
            VALUES
              (%(r_project)s, %(r_namespace)s, %(r_article)s, %(r_score)s,
               %(r_quality)s, %(r_quality_timestamp)s, %(r_importance)s,
               %(r_importance_timestamp)s)
        ''', attr.asdict(rating))
    self.wp10db.commit()

    logic_project.cleanup_project(self.wp10db, self.project)

  def test_deletes_empty(self):
    ratings = _get_all_ratings(self.wp10db)
    self.assertEqual(8, len(ratings))

    titles = set(r.r_article for r in ratings)
    self.assertTrue(b'Test results' not in titles, titles)
    self.assertTrue(b'Test main inheritance' not in titles, titles)
    self.assertTrue(b'Failures of tests' not in titles, titles)
    self.assertTrue(b'How to test' not in titles, titles)

  def test_updates_quality(self):
    ratings = _get_all_ratings(self.wp10db)
    for article in (b'Testing figures', b'Important tests'):
      for rating in ratings:
        if rating.r_article == article:
          self.assertEqual(self.not_a_class_db, rating.r_quality)

  def test_updates_importance(self):
    ratings = _get_all_ratings(self.wp10db)
    for article in (b'Testing history', b'Test practices'):
      for rating in ratings:
        if rating.r_article == article:
          self.assertEqual(self.not_a_class_db, rating.r_importance)


class UpdateProjectRecordTest(BaseWpOneDbTest):
  ratings = (
      (b'Art of testing', b'FA-Class', b'High-Class'),
      (b'Testing mechanics', b'FA-Class', b'Mid-Class'),
      (b'Rules of testing', b'FA-Class', b'NotA-Class'),
      (b'Test frameworks', b'NotA-Class', b'Mid-Class'),
      (b'Test practices', b'FL-Class', b'Unassessed-Class'),
      (b'Testing history', b'FL-Class', b'Unknown-Class'),
      (b'Testing figures', b'NotA-Class', b'Low-Class'),
      (b'Important tests', b'Unassessed-Class', b'Low-Class'),
  )

  def setUp(self):
    super().setUp()
    self.project = Project(p_project=b'Test', p_timestamp=b'20100101000000')

    qual_ts = b'2018-04-01T12:30:00Z'
    imp_ts = b'2018-05-01T13:45:10Z'
    with self.wp10db.cursor() as cursor:
      for r in self.ratings:
        rating = Rating(r_project=self.project.p_project,
                        r_namespace=0,
                        r_article=r[0],
                        r_quality=r[1],
                        r_importance=r[2],
                        r_quality_timestamp=qual_ts,
                        r_importance_timestamp=imp_ts)
        cursor.execute(
            '''
            INSERT INTO ratings
              (r_project, r_namespace, r_article, r_score, r_quality,
               r_quality_timestamp, r_importance, r_importance_timestamp)
            VALUES
              (%(r_project)s, %(r_namespace)s, %(r_article)s, %(r_score)s,
               %(r_quality)s, %(r_quality_timestamp)s, %(r_importance)s,
               %(r_importance_timestamp)s)
        ''', attr.asdict(rating))

    self.metadata = {
        'homepage': '/homepage',
        'shortname': 'Test',
        'parent': 'Nothing',
    }
    logic_project.update_project_record(self.wp10db, self.project,
                                        self.metadata)

  def test_metadata_correct(self):
    self.assertEqual(self.metadata['homepage'],
                     self.project.wikipage.decode('utf-8'))
    self.assertEqual(self.metadata['shortname'],
                     self.project.shortname.decode('utf-8'))
    self.assertEqual(self.metadata['parent'],
                     self.project.parent.decode('utf-8'))

  def test_count(self):
    self.assertEqual(8, self.project.p_count)

  def test_quality_count(self):
    self.assertEqual(5, self.project.p_qcount)

  def test_importance_count(self):
    self.assertEqual(6, self.project.p_icount)


class ProjectNamesTest(ArticlesTest):

  def _insert_categories(self):
    ts = datetime(2018, 12, 25, 11, 22, 33)
    root = ROOT_CATEGORY.encode('utf-8')
    pages = [(i, 'Test_%s_articles_by_quality' % i, root) for i in range(30)]
    with self.wikidb.cursor() as cursor:
      for p in pages:
        page_args = {'id': p[0], 'ns': CATEGORY_NS_INT, 'title': p[1]}
        cl_args = {'from': p[0], 'to': p[2], 'ts': ts}
        cursor.execute(
            '''
            INSERT INTO page
              (page_id, page_namespace, page_title)
            VALUES
              (%(id)s, %(ns)s, %(title)s)
        ''', page_args)
        cursor.execute(
            '''
            INSERT INTO categorylinks
              (cl_from, cl_to, cl_timestamp)
            VALUES
              (%(from)s, %(to)s, %(ts)s)
        ''', cl_args)
    self.wikidb.commit()

  def setUp(self):
    super().setUp()
    self._insert_categories()

  def test_project_names_to_update(self):
    name_list = list(logic_project.project_names_to_update(self.wikidb))
    self.assertEqual(30, len(name_list))


class GlobalCountAndListTest(BaseWpOneDbTest):

  def _insert_projects(self):
    with self.wp10db.cursor() as cursor:
      cursor.executemany(
          '''
          INSERT INTO projects
            (p_project, p_timestamp)
          VALUES
            (%s, '20181225001122')
      ''', [('Test Project %s' % i,) for i in range(50)])

  def setUp(self):
    super().setUp()
    self._insert_projects()

  @patch('wp1.logic.project.wp10_connect')
  @patch('wp1.logic.project.api')
  def test_global_count(self, patched_api, patched_connect):
    orig_close = self.wp10db.close
    try:
      self.wp10db.close = lambda: True
      patched_connect.return_value = self.wp10db
      logic_project.update_global_project_count()
      self.assertEqual(('50\n', 'Updating count: 50 projects'),
                       patched_api.save_page.call_args_list[0][0][1:])
    finally:
      self.wp10db.close = orig_close

  @patch('wp1.logic.project.wp10_connect')
  @patch('wp1.logic.project.api')
  def test_list_all_projects(self, patched_api, patched_connect):
    orig_close = self.wp10db.close
    try:
      self.wp10db.close = lambda: True
      patched_connect.return_value = self.wp10db
      projects = logic_project.list_all_projects(self.wp10db)
      self.assertEqual(50, len(projects))
    finally:
      self.wp10db.close = orig_close


class UpdateProjectByNameTest(BaseCombinedDbTest):

  def _insert_project(self):
    with self.wp10db.cursor() as cursor:
      cursor.execute(
          '''
          INSERT INTO projects
            (p_project, p_timestamp)
          VALUES
            (%s, '20181225001122')
      ''', ('Test Projecct',))

  def setUp(self):
    super().setUp()
    self._insert_project()

  @patch('wp1.logic.project.redis_connect')
  @patch('wp1.logic.project.wiki_connect')
  @patch('wp1.logic.project.wp10_connect')
  @patch('wp1.logic.project.update_project')
  def test_calls_update_project_with_existing(self, patched_update_project,
                                              patched_wp10_connect,
                                              patched_wiki_connect,
                                              patched_redis_connect):
    orig_wp10_close = self.wp10db.close
    orig_wiki_close = self.wikidb.close
    try:
      self.wp10db.close = lambda: True
      self.wikidb.close = lambda: True
      patched_wp10_connect.return_value = self.wp10db
      patched_wiki_connect.return_value = self.wikidb
      patched_redis_connect.return_value = fakeredis.FakeStrictRedis()

      logic_project.update_project_by_name(b'Test Project')
      patched_update_project.assert_called_once()
    finally:
      self.wp10db.close = orig_wp10_close
      self.wikidb.close = orig_wiki_close

  @patch('wp1.logic.project.redis_connect')
  @patch('wp1.logic.project.wiki_connect')
  @patch('wp1.logic.project.wp10_connect')
  @patch('wp1.logic.project.update_project')
  def test_calls_update_project_manual(self, patched_update_project,
                                       patched_wp10_connect,
                                       patched_wiki_connect,
                                       patched_redis_connect):
    orig_wp10_close = self.wp10db.close
    orig_wiki_close = self.wikidb.close
    try:
      self.wp10db.close = lambda: True
      self.wikidb.close = lambda: True
      redis_mock = MagicMock()
      patched_wp10_connect.return_value = self.wp10db
      patched_wiki_connect.return_value = self.wikidb
      patched_redis_connect.return_value = redis_mock

      logic_project.update_project_by_name(b'Test Project', track_progress=True)
      redis_mock.expire.assert_called_once()
    finally:
      self.wp10db.close = orig_wp10_close
      self.wikidb.close = orig_wiki_close

  @patch('wp1.logic.project.redis_connect')
  @patch('wp1.logic.project.wiki_connect')
  @patch('wp1.logic.project.wp10_connect')
  @patch('wp1.logic.project.update_project')
  def test_creates_new(self, patched_update_project, patched_wp10_connect,
                       patched_wiki_connect, patched_redis_connect):
    orig_wp10_close = self.wp10db.close
    orig_wiki_close = self.wikidb.close
    try:
      self.wp10db.close = lambda: True
      self.wikidb.close = lambda: True
      patched_wp10_connect.return_value = self.wp10db
      patched_wiki_connect.return_value = self.wikidb
      patched_redis_connect.return_value = fakeredis.FakeStrictRedis()

      logic_project.update_project_by_name(b'Foo New Project')
      patched_update_project.assert_called_once()
    finally:
      self.wp10db.close = orig_wp10_close
      self.wikidb.close = orig_wiki_close


class ProjectProgressTest(ArticlesTest):

  def setUp(self):
    super().setUp()
    self._insert_pages(self.quality_pages)
    self._insert_pages(self.importance_pages)
    self._insert_ratings(zip(self.quality_pages[6:], self.importance_pages[4:]),
                         0, 'both')
    self.redis = fakeredis.FakeStrictRedis()

  def test_initial_work_count(self):
    logic_project.update_project_assessments(self.wikidb,
                                             self.wp10db,
                                             self.project, {},
                                             redis=self.redis,
                                             track_progress=True)
    actual = self.redis.hget(b'progress:%s' % self.project.p_project, 'work')
    self.assertEqual(b'34', actual)

  def test_final_progress(self):
    logic_project.update_project_assessments(self.wikidb,
                                             self.wp10db,
                                             self.project, {},
                                             redis=self.redis,
                                             track_progress=True)
    actual = self.redis.hget(b'progress:%s' % self.project.p_project,
                             'progress')
    self.assertEqual(b'36', actual)
