from lucky.base_orm_test import BaseWpOneOrmTest
from lucky.conf import get_conf
from lucky.constants import AssessmentKind
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
