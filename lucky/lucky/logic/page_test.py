from datetime import datetime

from lucky.base_orm_test import BaseWikiOrmTest
from lucky.logic import page as logic_page
from lucky.models.wiki.page import Page

class LogicPageCategoryTest(BaseWikiOrmTest):
  def setUp(self):
    super().setUp()
    ts = datetime(2018, 9, 30, 12, 30, 0)
    self.session.execute('''
      INSERT INTO page (page_id, page_namespace, page_title)
      VALUES (:id, :ns, :title)
    ''', [
      {'id': 100, 'ns': 0, 'title': b'The cape of Superman'},
      {'id': 101, 'ns': 0, 'title': b'Powers of Superman'},
      {'id': 102, 'ns': 14, 'title': b'Places Superman vacations'},
      {'id': 103, 'ns': 14, 'title': b'Superman Facts'},
    ])
    self.session.execute('''
      INSERT INTO categorylinks (cl_from, cl_to, cl_timestamp)
      VALUES (:from, :to, :timestamp)
    ''', [
      {'from': 100, 'to': b'Articles about Superman', 'timestamp': ts},
      {'from': 101, 'to': b'Articles about Superman', 'timestamp': ts},
      {'from': 102, 'to': b'Articles about Superman', 'timestamp': ts},
      {'from': 103, 'to': b'Articles about Superman', 'timestamp': ts},
    ])
    self.session.commit()
    
  def test_get_category_pages(self):
    titles = set()
    for page in logic_page.get_pages_by_category(
        self.session, b'Articles about Superman'):
      titles.add(page.title)

    self.assertEqual(4, len(titles))
    self.assertTrue(b'The cape of Superman' in titles)
    self.assertTrue(b'Powers of Superman' in titles)
    self.assertTrue(b'Places Superman vacations' in titles)
    self.assertTrue(b'Superman Facts' in titles)

  def test_get_category_pages_ns_filter(self):
    titles = set()
    for page in logic_page.get_pages_by_category(
        self.session, b'Articles about Superman', ns=14):
      print(page.namespace)
      titles.add(page.title)

    print(titles)
    self.assertEqual(2, len(titles))
    self.assertTrue(b'Superman Facts' in titles)
    self.assertTrue(b'Places Superman vacations' in titles)
