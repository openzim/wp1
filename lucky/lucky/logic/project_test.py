from lucky.base_orm_test import BaseWpOneOrmTest, BaseCombinedOrmTest
from lucky.conf import get_conf
from lucky.constants import AssessmentKind, CATEGORY_NS_INT
from lucky.logic import project as logic_project
from lucky.models.wiki.page import Page
from lucky.models.wp10.category import Category
from lucky.models.wp10.project import Project

config = get_conf()
QUALITY = config['QUALITY']
IMPORTANCE = config['IMPORTANCE']

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
