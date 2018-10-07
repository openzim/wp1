from datetime import datetime
from unittest.mock import patch

from lucky.base_orm_test import BaseWpOneOrmTest, BaseCombinedOrmTest
from lucky.conf import get_conf
from lucky.constants import AssessmentKind, CATEGORY_NS_INT, GLOBAL_TIMESTAMP_WIKI, TS_FORMAT
from lucky.logic import project as logic_project
from lucky.models.wiki.page import Page
from lucky.models.wp10.category import Category
from lucky.models.wp10.project import Project
from lucky.models.wp10.rating import Rating

config = get_conf()
QUALITY = config['QUALITY']
IMPORTANCE = config['IMPORTANCE']
NOT_A_CLASS = config['NOT_A_CLASS']

class UpdateCategoryTest(BaseWpOneOrmTest):
  def setUp(self):
    super().setUp()
    self.project = Project(project=b'Test Project')
    self.page = Page(title=b'A-Class Test articles')
    self.page_1 = Page(title=b'Mid-importance Test articles')
    self.page_2 = Page(title=b'Draft-Class Test articles')

  def test_quality_gets_updated(self):
    rating_to_category = {}
    logic_project.update_category(
      self.session, self.project, self.page, {}, AssessmentKind.QUALITY,
      rating_to_category)
    self.session.commit()

    category = self.session.query(Category).first()
    self.assertEqual(self.page.title, rating_to_category['A-Class'])
    self.assertEqual(self.project.project, category.project)
    self.assertEqual(b'quality', category.type)
    self.assertEqual(b'A-Class', category.rating)
    self.assertEqual(self.page.title, category.category)
    self.assertEqual(QUALITY['A-Class'], category.ranking)
    self.assertEqual(b'A-Class', category.replacement)

  def test_importance_gets_updated(self):
    rating_to_category = {}
    logic_project.update_category(
      self.session, self.project, self.page_1, {}, AssessmentKind.IMPORTANCE,
      rating_to_category)
    self.session.commit()

    category = self.session.query(Category).first()
    self.assertEqual(self.page_1.title, rating_to_category['Mid-Class'])
    self.assertEqual(self.project.project, category.project)
    self.assertEqual(b'importance', category.type)
    self.assertEqual(b'Mid-Class', category.rating)
    self.assertEqual(self.page_1.title, category.category)
    self.assertEqual(IMPORTANCE['Mid-Class'], category.ranking)
    self.assertEqual(b'Mid-Class', category.replacement)

  def test_extra_category_gets_updated(self):
    rating_to_category = {}
    extra = {
      self.page_2.title: {
        'title': 'Draft-Class',
        'ranking': 10,
        'replaces': 'Disambig-Class'
      }
    }
    logic_project.update_category(
      self.session, self.project, self.page_2, extra, AssessmentKind.QUALITY,
      rating_to_category)
    self.session.commit()

    category = self.session.query(Category).first()
    self.assertEqual(self.page_2.title, rating_to_category['Draft-Class'])
    self.assertEqual(self.project.project, category.project)
    self.assertEqual(b'quality', category.type)
    self.assertEqual(b'Draft-Class', category.rating)
    self.assertEqual(self.page_2.title, category.category)
    self.assertEqual(10, category.ranking)
    self.assertEqual(b'Disambig-Class', category.replacement)

  def test_skips_page_with_no_mapping_match(self):
    rating_to_category = {}
    logic_project.update_category(
      self.session, self.project, Page(title=b'123*go'), {},
      AssessmentKind.QUALITY, rating_to_category)
    self.session.commit()

    category = self.session.query(Category).first()
    self.assertIsNone(category)
    self.assertEqual(0, len(rating_to_category))
    
  def test_skips_page_with_no_class_match(self):
    rating_to_category = {}
    logic_project.update_category(
      self.session, self.project, Page(title=b'Foo-Class Test articles'), {},
      AssessmentKind.QUALITY, rating_to_category)
    self.session.commit()

    category = self.session.query(Category).first()
    self.assertIsNone(category)
    self.assertEqual(0, len(rating_to_category))

class UpdateProjectCategoriesByKindTest(BaseCombinedOrmTest):
  quality_pages = (
    (101, b'FA-Class_Test_articles', b'Test_articles_by_quality', b'FA-Class'),
    (102, b'FL-Class_Test_articles', b'Test_articles_by_quality', b'FL-Class'),
    (103, b'A-Class_Test_articles', b'Test_articles_by_quality', b'A-Class'),
    (104, b'GA-Class_Test_articles', b'Test_articles_by_quality', b'GA-Class'),
    (105, b'B-Class_Test_articles', b'Test_articles_by_quality', b'B-Class'),
    (106, b'C-Class_Test_articles', b'Test_articles_by_quality', b'C-Class'),
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
    for p in pages:
      self.wiki_session.execute('''
        INSERT INTO page (page_id, page_namespace, page_title)
        VALUES (:id, :ns, :title)
      ''', [
        {'id': p[0], 'ns': 14, 'title': p[1]},
      ])
      self.wiki_session.execute('''
        INSERT INTO categorylinks (cl_from, cl_to)
        VALUES (:from, :to)
      ''', [
        {'from': p[0], 'to': p[2]},
      ])

  def setUp(self):
    super().setUp()
    self.project = Project(project=b'Test')
    self._insert_pages(self.additional_junk_pages)

  def test_update_quality(self):
    self._insert_pages(self.quality_pages)
    logic_project.update_project_categories_by_kind(
      self.wiki_session, self.wp10_session, self.project, {},
      AssessmentKind.QUALITY)

    categories = self.wp10_session.query(Category).all()
    self.assertNotEqual(0, len(categories))
    for category in categories:
      self.assertEqual(self.project.project, category.project)
      self.assertEqual(b'quality', category.type)

    category_titles = set(category.category for category in categories)
    expected_titles = set(p[1] for p in self.quality_pages)
    self.assertEqual(expected_titles, category_titles)

    category_ratings = set(category.rating for category in categories)
    expected_ratings = set(p[3] for p in self.quality_pages)
    self.assertEqual(expected_ratings, category_ratings)

    category_replaces = set(category.replacement for category in categories)
    self.assertEqual(expected_ratings, category_replaces)

  def test_update_quality_rating_to_category(self):
    self._insert_pages(self.quality_pages)
    rating_to_category = logic_project.update_project_categories_by_kind(
      self.wiki_session, self.wp10_session, self.project, {},
      AssessmentKind.QUALITY)

    expected = dict((p[3].decode('utf-8'), p[1]) for p in self.quality_pages)
    self.assertEqual(expected, rating_to_category)

  def test_update_importance(self):
    self._insert_pages(self.importance_pages)
    logic_project.update_project_categories_by_kind(
      self.wiki_session, self.wp10_session, self.project, {},
      AssessmentKind.IMPORTANCE)

    categories = self.wp10_session.query(Category).all()
    self.assertNotEqual(0, len(categories))
    print(repr(categories))
    for category in categories:
      self.assertEqual(self.project.project, category.project)
      self.assertEqual(b'importance', category.type)

    category_titles = set(category.category for category in categories)
    expected_titles = set(p[1] for p in self.importance_pages)
    self.assertEqual(expected_titles, category_titles)

    category_ratings = set(category.rating for category in categories)
    expected_ratings = set(p[3] for p in self.importance_pages)
    self.assertEqual(expected_ratings, category_ratings)

    category_replaces = set(category.replacement for category in categories)
    self.assertEqual(expected_ratings, category_replaces)

  def test_update_priority(self):
    self._insert_pages(self.priority_pages)
    logic_project.update_project_categories_by_kind(
      self.wiki_session, self.wp10_session, self.project, {},
      AssessmentKind.IMPORTANCE)

    categories = self.wp10_session.query(Category).all()
    self.assertNotEqual(0, len(categories))
    for category in categories:
      self.assertEqual(self.project.project, category.project)
      self.assertEqual(b'importance', category.type)

    category_titles = set(category.category for category in categories)
    expected_titles = set(p[1] for p in self.priority_pages)
    self.assertEqual(expected_titles, category_titles)

    category_ratings = set(category.rating for category in categories)
    expected_ratings = set(p[3] for p in self.priority_pages)
    self.assertEqual(expected_ratings, category_ratings)

    category_replaces = set(category.replacement for category in categories)
    self.assertEqual(expected_ratings, category_replaces)

class UpdateProjectAssessmentsTest(BaseCombinedOrmTest):
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
    (230, b'Test main inheritance', b'GA-Class_Test_articles', b'GA-Class', 1),
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
    (2320, b'Test other inheritance', b'Mid-Class_Test_articles', b'Mid-Class',
     1),
    (2400, b'Testing best practices', b'Low-Class_Test_articles', b'Low-Class',
     1),
    (2410, b'Testing tools', b'Low-Class_Test_articles', b'Low-Class', 1),
    (2420, b'Operation of tests', b'Low-Class_Test_articles', b'Low-Class', 1),
    (2500, b'Lesser-known tests', b'Low-Class_Test_articles', b'Low-Class', 1),
    (2510, b'Failures of tests', b'Low-Class_Test_articles', b'Low-Class', 1),
    (2520, b'How to test', b'Low-Class_Test_articles', b'Low-Class', 1),
  )

  def _insert_pages(self, pages):
    ts = datetime.now()
    for p in pages:
      self.wiki_session.execute('''
        INSERT INTO page (page_id, page_namespace, page_title)
        VALUES (:id, :ns, :title)
      ''', [
        {'id': p[0], 'ns': p[4], 'title': p[1]},
      ])
      self.wiki_session.execute('''
        INSERT INTO categorylinks (cl_from, cl_to, cl_timestamp)
        VALUES (:from, :to, :ts)
      ''', [
        {'from': p[0], 'to': p[2], 'ts': ts},
      ])  

  def _insert_ratings(self, pages, namespace, kind, override_rating=None):
    for p in pages:
      r = p[3]
      if override_rating is not None:
        r = override_rating
      rating = Rating(
        project=self.project.project, namespace=namespace, article=p[1])
      if kind == AssessmentKind.QUALITY or kind == 'both':
        rating.quality = r
        rating.quality_timestamp = GLOBAL_TIMESTAMP_WIKI
      elif kind == AssessmentKind.IMPORTANCE or kind == 'both':
        rating.importance=r
        rating.importance_timestamp=GLOBAL_TIMESTAMP_WIKI
      self.wp10_session.add(rating)
    self.wp10_session.commit()

  def setUp(self):
    super().setUp()
    self.project = Project(project=b'Test', timestamp=b'2010-01-01T00:00:00Z')

    self.timestamp_str = '2011-04-28T12:30:00Z'
    self.expected_ns = 0
    self.expected_title = 'Test Moving'
    self.expected_dt = datetime.strptime(self.timestamp_str, TS_FORMAT)

    self.api_return = {
      'query': {
        'redirects': [{'to': self.expected_title}],
        'pages': {123: {
          'ns': self.expected_ns,
          'title': self.expected_title,
          'revisions': [{'timestamp': self.timestamp_str}],
        }},
      },
    }


  def test_old_rating_same_quality(self):
    self._insert_pages(self.quality_pages)
    self._insert_ratings(self.quality_pages[6:], 0, AssessmentKind.QUALITY)

    logic_project.update_project_assessments(
      self.wiki_session, self.wp10_session, self.project, {},
      AssessmentKind.QUALITY)

    ratings = self.wp10_session.query(Rating).all()
    self.assertNotEqual(0, len(ratings))

    pages = self.quality_pages[6:]
    expected_titles = set(p[1] for p in pages)
    actual_titles = set(r.article for r in ratings)
    self.assertEqual(expected_titles, actual_titles)

    page_to_rating = dict((p[1], p[3]) for p in pages)
    for r in ratings:
      self.assertEqual(page_to_rating[r.article], r.quality)

  def test_old_rating_same_importance(self):
    self._insert_pages(self.importance_pages)
    self._insert_ratings(
      self.importance_pages[4:], 0, AssessmentKind.IMPORTANCE)

    logic_project.update_project_assessments(
      self.wiki_session, self.wp10_session, self.project, {},
      AssessmentKind.IMPORTANCE)

    ratings = self.wp10_session.query(Rating).all()
    self.assertNotEqual(0, len(ratings))

    pages = self.importance_pages[4:]
    expected_titles = set(p[1] for p in pages)
    actual_titles = set(r.article for r in ratings)
    self.assertEqual(expected_titles, actual_titles)

    page_to_rating = dict((p[1], p[3]) for p in pages)
    for r in ratings:
      self.assertEqual(page_to_rating[r.article], r.importance)

  def test_old_rating_update_quality(self):
    self._insert_pages(self.quality_pages)
    self._insert_ratings(
      self.quality_pages[6:], 0, AssessmentKind.QUALITY,
      override_rating=NOT_A_CLASS.encode('utf-8'))

    logic_project.update_project_assessments(
      self.wiki_session, self.wp10_session, self.project, {},
      AssessmentKind.QUALITY)

    ratings = self.wp10_session.query(Rating).all()
    self.assertNotEqual(0, len(ratings))

    pages = self.quality_pages[6:]
    expected_titles = set(p[1] for p in pages)
    actual_titles = set(r.article for r in ratings)
    self.assertEqual(expected_titles, actual_titles)

    page_to_rating = dict((p[1], p[3]) for p in pages)
    for r in ratings:
      self.assertEqual(page_to_rating[r.article], r.quality)

  def test_old_rating_update_importance(self):
    self._insert_pages(self.importance_pages)
    self._insert_ratings(
      self.importance_pages[4:], 0, AssessmentKind.IMPORTANCE,
      override_rating=NOT_A_CLASS.encode('utf-8'))

    logic_project.update_project_assessments(
      self.wiki_session, self.wp10_session, self.project, {},
      AssessmentKind.IMPORTANCE)

    ratings = self.wp10_session.query(Rating).all()
    self.assertNotEqual(0, len(ratings))

    pages = self.importance_pages[4:]
    expected_titles = set(p[1] for p in pages)
    actual_titles = set(r.article for r in ratings)
    self.assertEqual(expected_titles, actual_titles)

    page_to_rating = dict((p[1], p[3]) for p in pages)
    for r in ratings:
      self.assertEqual(page_to_rating[r.article], r.importance)

  def test_old_rating_update_both(self):
    self._insert_pages(self.quality_pages)
    self._insert_pages(self.importance_pages)
    self._insert_ratings(
      self.quality_pages[6:], 0, 'both',
      override_rating=NOT_A_CLASS.encode('utf-8'))

    logic_project.update_project_assessments(
      self.wiki_session, self.wp10_session, self.project, {},
      AssessmentKind.QUALITY)
    logic_project.update_project_assessments(
      self.wiki_session, self.wp10_session, self.project, {},
      AssessmentKind.IMPORTANCE)

    ratings = self.wp10_session.query(Rating).all()
    self.assertNotEqual(0, len(ratings))

    q_pages = self.quality_pages[6:]
    i_pages = self.importance_pages[4:]
    expected_titles = set(p[1] for p in q_pages)
    actual_titles = set(r.article for r in ratings)
    self.assertEqual(expected_titles, actual_titles)

    q_page_to_rating = dict((p[1], p[3]) for p in q_pages)
    i_page_to_rating = dict((p[1], p[3]) for p in i_pages)
    for r in ratings:
      self.assertEqual(q_page_to_rating[r.article], r.quality)
      self.assertEqual(i_page_to_rating[r.article], r.importance)

  @patch('lucky.logic.api.page.site')
  def test_not_seen_quality(self, patched_site):
    self._insert_pages(self.quality_pages[:-2])
    self._insert_ratings(self.quality_pages[6:], 0, AssessmentKind.QUALITY)

    def fake_api(*args, **kwargs):
      if kwargs['titles'] == ':How to test':
        return self.api_return
      return {}
    patched_site.api.side_effect = fake_api

    logic_project.update_project_assessments(
      self.wiki_session, self.wp10_session, self.project, {},
      AssessmentKind.QUALITY)

    ratings = self.wp10_session.query(Rating).all()
    self.assertNotEqual(0, len(ratings))

    pages = self.quality_pages[6:]
    expected_titles = set(p[1] for p in pages)
    actual_titles = set(r.article for r in ratings)
    self.assertEqual(expected_titles, actual_titles)

    page_to_rating = dict((p[1], p[3]) for p in pages)
    for r in ratings:
      if r.article in (b'How to test', b'Failures of tests'):
        self.assertEqual(NOT_A_CLASS.encode('utf-8'), r.quality)
      else:
        self.assertEqual(page_to_rating[r.article], r.quality)

  @patch('lucky.logic.api.page.site')
  def test_not_seen_importance(self, patched_site):
    self._insert_pages(self.importance_pages[:-2])
    self._insert_ratings(
      self.importance_pages[4:], 0, AssessmentKind.IMPORTANCE)

    def fake_api(*args, **kwargs):
      if kwargs['titles'] == ':How to test':
        return self.api_return
      return {}
    patched_site.api.side_effect = fake_api

    logic_project.update_project_assessments(
      self.wiki_session, self.wp10_session, self.project, {},
      AssessmentKind.IMPORTANCE)

    ratings = self.wp10_session.query(Rating).all()
    self.assertNotEqual(0, len(ratings))

    pages = self.importance_pages[4:]
    expected_titles = set(p[1] for p in pages)
    actual_titles = set(r.article for r in ratings)
    self.assertEqual(expected_titles, actual_titles)

    page_to_rating = dict((p[1], p[3]) for p in pages)
    for r in ratings:
      if r.article in (b'How to test', b'Failures of tests'):
        self.assertEqual(NOT_A_CLASS.encode('utf-8'), r.importance)
      else:
        self.assertEqual(page_to_rating[r.article], r.importance, repr(r))

class CleanupProjectTest(BaseWpOneOrmTest):
  ratings = (
    (b'Art of testing', b'FA-Class', b'High-Class'),
    (b'Testing mechanics', b'FA-Class', b'Mid-Class'),
    (b'Rules of testing',  b'FA-Class', b'NotA-Class'),
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
    self.project = Project(project=b'Test')

    qual_ts = b'2018-04-01T12:30:00Z'
    imp_ts = b'2018-05-01T13:45:10Z'

    for r in self.ratings:
      rating = Rating(project=self.project.project, namespace=0, article=r[0],
                      quality=r[1], importance=r[2], quality_timestamp=qual_ts,
                      importance_timestamp=imp_ts)
      self.session.add(rating)
    self.session.commit()
      
    logic_project.cleanup_project(self.session, self.project)
    self.session.commit()

  def test_deletes_empty(self):
    ratings = self.session.query(Rating).all()
    self.assertEqual(8, len(ratings))

    titles = set(r.article for r in ratings)
    self.assertTrue(b'Test results' not in titles, titles)
    self.assertTrue(b'Test main inheritance' not in titles, titles)
    self.assertTrue(b'Failures of tests' not in titles, titles)
    self.assertTrue(b'How to test' not in titles, titles)
    
  def test_updates_quality(self):
    for article in (b'Testing figures', b'Important tests'):
      rating = self.session.query(Rating).filter(
        Rating.article == article).first()
      self.assertEqual(self.not_a_class_db, rating.quality)

  def test_updates_importance(self):
    for article in (b'Testing history', b'Test practices'):
      rating = self.session.query(Rating).filter(
        Rating.article == article).first()
      self.assertEqual(self.not_a_class_db, rating.importance)
