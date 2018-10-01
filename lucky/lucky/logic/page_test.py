from datetime import datetime
from unittest.mock import patch
import time

from lucky.base_orm_test import BaseWikiOrmTest, BaseWpOneOrmTest
from lucky.constants import TS_FORMAT
from lucky.logic import page as logic_page
from lucky.models.wp10.namespace import Namespace, NsType
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


class LogicPageMovesTest(BaseWpOneOrmTest):
  def setUp(self):
    super().setUp()
    n = Namespace(dbname=b'enwiki_p', domain=b'en.wikipedia.org', id=0,
                  name=b'', type=NsType.primary)
    self.session.add(n)
    self.session.commit()

    self.timestamp_str = '2011-04-28T12:30:00Z'
    self.expected_ns = 0
    self.expected_title = 'Article moved to'
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

    self.le_return = [{
      'params': {
        'target_ns': self.expected_ns,
        'target_title': self.expected_title,
      },
      'timestamp': time.strptime(self.timestamp_str, TS_FORMAT),
    }]

    self.le_multi = [{
      'params': {
        'target_ns': self.expected_ns,
        'target_title': self.expected_title,
      },
      'timestamp': time.strptime(self.timestamp_str, TS_FORMAT),
    }, {
      'params': {
        'target_ns': self.expected_ns + 10,
        'target_title': 'Some other article',
      },
      'timestamp': time.strptime('2010-08-08T12:30:00Z', TS_FORMAT),
    }, {
      'params': {
        'target_ns': self.expected_ns + 20,
        'target_title': 'Another crazy article',
      },
      'timestamp': time.strptime('2008-08-08T12:30:00Z', TS_FORMAT),
  }]

  @patch('lucky.logic.api.page.site')
  def test_no_redirect_no_move(self, unused_patched_site):
    move_data = logic_page.get_move_data(
      self.session, 0, b'Some Moved Article', datetime(1970, 1, 1))
    self.assertIsNone(move_data)

  @patch('lucky.logic.api.page.site')
  def test_get_redirect_from_api(self, patched_site):
    patched_site.api.side_effect = lambda *args, **kwargs: self.api_return
    move_data = logic_page.get_move_data(
      self.session, 0, b'Some Moved Article', datetime(1970, 1, 1))

    self.assertIsNotNone(move_data)
    self.assertEqual(self.expected_ns, move_data['dest_ns'])
    self.assertEqual(self.expected_title.encode('utf-8'),
                     move_data['dest_title'])
    self.assertEqual(self.expected_dt, move_data['timestamp_dt'])

  @patch('lucky.logic.api.page.site')
  def test_get_single_move_from_api(self, patched_site):
    patched_site.logevents.side_effect = lambda *args, **kwargs: self.le_return
    move_data = logic_page.get_move_data(
      self.session, 0, b'Some Moved Article', datetime(1970, 1, 1))

    self.assertIsNotNone(move_data)
    self.assertEqual(self.expected_ns, move_data['dest_ns'])
    self.assertEqual(self.expected_title.encode('utf-8'),
                     move_data['dest_title'])
    self.assertEqual(self.expected_dt, move_data['timestamp_dt'])

  @patch('lucky.logic.api.page.site')
  def test_get_most_recent_move_from_api(self, patched_site):
    patched_site.logevents.side_effect = lambda *args, **kwargs: self.le_multi
    move_data = logic_page.get_move_data(
      self.session, 0, b'Some Moved Article', datetime(1970, 1, 1))

    self.assertIsNotNone(move_data)
    self.assertEqual(self.expected_ns, move_data['dest_ns'])
    self.assertEqual(self.expected_title.encode('utf-8'),
                     move_data['dest_title'])
    self.assertEqual(self.expected_dt, move_data['timestamp_dt'])

  @patch('lucky.logic.api.page.site')
  def test_get_redirect_too_old_from_api(self, patched_site):
    patched_site.api.side_effect = lambda *args, **kwargs: self.api_return
    move_data = logic_page.get_move_data(
      self.session, 0, b'Some Moved Article', datetime(2014, 1, 1))
    self.assertIsNone(move_data)
    
  @patch('lucky.logic.api.page.site')
  def test_get_single_move_too_old_from_api(self, patched_site):
    patched_site.logevents.side_effect = lambda *args, **kwargs: self.le_return
    move_data = logic_page.get_move_data(
      self.session, 0, b'Some Moved Article', datetime(2014, 1, 1))
    self.assertIsNone(move_data)
