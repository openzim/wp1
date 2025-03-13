from collections import defaultdict
from datetime import datetime
from unittest.mock import patch

import attr

from wp1 import logs
from wp1.base_db_test import BaseCombinedDbTest
from wp1.models.wp10.log import Log


class LogsTest(BaseCombinedDbTest):
  project = b'Catholicism'

  articles = [
      # The IDs of these pages are set equal to the length of their titles, so if
      # you add a new one, make sure it has a differing length or you might have
      # weird errors.
      (b'Test practices', b'Unknown-Class', b'Category-Class', b'NotA-Class',
       b'NotA-Class', 14),
      (b'Testing mechanics', b'NotA-Class', b'Category-Class', b'NotA-Class',
       b'NotA-Class', 14),
      (b'Test results', b'GA-Class', b'NotA-Class', b'Mid-Class',
       b'NotA-Class'),
      (b'Testing tools', b'B-Class', b'NotA-Class'),
      (b'Art of testing', b'A-Class', b'FA-Class', b'Mid-Class', b'High-Class'),
      (b'Rules of testing', b'B-Class', b'FA-Class'),
      (b'Testing history', b'Unassessed-Class', b'FL-Class'),
      (b'Test frameworks', b'NotA-Class', b'FL-Class'),
      (b'Testing figures', b'NotA-Class', b'A-Class', b'NotA-Class',
       b'Low-Class'),
      (b'Important tests', b'NotA-Class', b'NotA-Class', b'Unknown-Class',
       b'Low-Class'),
      (b'Test main inheritance', b'NotA-Class', b'NotA-Class', b'NotA-Class',
       b'Low-Class'),
      (b'Test sub inheritance', b'Unknown-Class', b'GA-Class'),
      (b'Test other inheritance', b'Unknown-Class', b'B-Class'),
      (b'Testing best practices', b'C-Class', b'B-Class'),
      (b'Operation of tests', b'B-Class', b'Unassessed-Class', b'Mid-Class',
       b'Unassessed-Class'),
      (b'Lesser-known tests', b'Stub-Class', b'Start-Class', b'Unknown-Class',
       b'Mid-Class'),
      (b'Failures of tests', b'C-Class', b'C-Class'),
      (b'How to test', b'Stub-Class', b'C-Class', b'NotA-Class',
       b'Unknown-Class'),
      (b'Testing None-a', None, None, None, None),
      (b'Testing None-ab', None, b'Stub-Class', None, b'Unknown-Class'),
      (b'Test for None-abc', None, None, b'Unknown-Class', b'Mid-Class'),
  ]

  moves = [
      (b'Testing in Copenhaven', b'Testing in Copenhagen'),
      (b'Tests', b'Tests (software)'),
      (b'Test Foo Bar', b'Test Foo'),
      (b'Test Baz Bang', b'Test Baz'),
  ]

  timestamps = [
      b'20181225112233',
      b'20181226101010',
      b'20181227130000',
  ]
  wiki_timestamps = [
      b'2018-12-25T08:22:33Z',
      b'2018-12-26T05:10:10Z',
      b'2018-12-27T08:00:00Z',
  ]

  def _logs(self):
    logs = []
    for i, a in enumerate(self.articles):
      ts = self.timestamps[i % len(self.timestamps)]
      wiki_ts = self.wiki_timestamps[i % len(self.wiki_timestamps)]
      if len(a) == 6:
        ns = a[5]
      else:
        ns = 0

      if len(a) >= 3:
        if a[1] is not None and a[2] is not None:
          l = Log(l_project=self.project,
                  l_article=a[0],
                  l_action=b'quality',
                  l_old=a[1],
                  l_new=a[2],
                  l_namespace=ns,
                  l_timestamp=ts,
                  l_revision_timestamp=wiki_ts)
          logs.append(l)
      if len(a) == 5:
        l = Log(l_project=self.project,
                l_article=a[0],
                l_action=b'importance',
                l_old=a[2],
                l_new=a[3],
                l_namespace=ns,
                l_timestamp=ts,
                l_revision_timestamp=wiki_ts)
        logs.append(l)
    return logs

  def _move_logs(self):
    logs = []
    for i, m in enumerate(self.moves):
      ts = self.timestamps[i % len(self.timestamps)]
      wiki_ts = self.wiki_timestamps[i % len(self.wiki_timestamps)]

      l = Log(l_project=self.project,
              l_article=m[0],
              l_action=b'moved',
              l_old=None,
              l_new=None,
              l_namespace=0,
              l_timestamp=ts,
              l_revision_timestamp=wiki_ts)
      logs.append(l)
    return logs

  def _insert_logs(self, logs=None):
    with self.wp10db.cursor() as cursor:
      cursor.executemany(
          '''
        INSERT INTO logging
           (l_project, l_namespace, l_article, l_old, l_new, l_action,
           l_timestamp, l_revision_timestamp)
        VALUES
          (%(l_project)s, %(l_namespace)s, %(l_article)s, %(l_old)s, %(l_new)s,
           %(l_action)s, %(l_timestamp)s, %(l_revision_timestamp)s)
      ''', [attr.asdict(log) for log in logs])
    self.wp10db.commit()

  def _insert_moves(self):
    move_data = [(0, m[0], 0, m[1],
                  self.wiki_timestamps[i % len(self.wiki_timestamps)])
                 for i, m in enumerate(self.moves)]
    with self.wp10db.cursor() as cursor:
      cursor.executemany(
          '''
        INSERT INTO moves
          (m_old_namespace, m_old_article, m_new_namespace, m_new_article,
           m_timestamp)
        VALUES
          (%s, %s, %s, %s, %s)
      ''', move_data)
    self._insert_logs(self._move_logs())

  def _insert_revids(self):
    with self.wikidb.cursor() as cursor:
      cursor.executemany(
          '''
        INSERT INTO page (page_id, page_namespace, page_title)
        VALUES (%s, %s, %s)
      ''', [(len(a[0]), 0 if len(a) < 6 else 14, a[0]) for a in self.articles])
      cursor.executemany(
          '''
        INSERT INTO revision
          (rev_page, rev_timestamp, rev_id)
        VALUES
          (%s, %s, %s)
      ''', [(len(a[0]), b'20181219010203', '%s000' % len(a[0]))
            for a in self.articles])

  def setUp(self):
    super().setUp()
    self._insert_logs(self._logs())
    self._insert_moves()
    self._insert_revids()

  def test_get_logs(self):
    expected = [
        (b'Catholicism', 0, b'Art of testing', b'importance', b'20181226101010',
         b'FA-Class', b'Mid-Class', b'2018-12-26T05:10:10Z'),
        (b'Catholicism', 0, b'Art of testing', b'quality', b'20181226101010',
         b'A-Class', b'FA-Class', b'2018-12-26T05:10:10Z'),
        (b'Catholicism', 0, b'Failures of tests', b'quality', b'20181226101010',
         b'C-Class', b'C-Class', b'2018-12-26T05:10:10Z'),
        (b'Catholicism', 0, b'How to test', b'importance', b'20181227130000',
         b'C-Class', b'NotA-Class', b'2018-12-27T08:00:00Z'),
        (b'Catholicism', 0, b'How to test', b'quality', b'20181227130000',
         b'Stub-Class', b'C-Class', b'2018-12-27T08:00:00Z'),
        (b'Catholicism', 0, b'Important tests', b'importance',
         b'20181225112233', b'NotA-Class', b'Unknown-Class',
         b'2018-12-25T08:22:33Z'),
        (b'Catholicism', 0, b'Important tests', b'quality', b'20181225112233',
         b'NotA-Class', b'NotA-Class', b'2018-12-25T08:22:33Z'),
        (b'Catholicism', 0, b'Lesser-known tests', b'importance',
         b'20181225112233', b'Start-Class', b'Unknown-Class',
         b'2018-12-25T08:22:33Z'),
        (b'Catholicism', 0, b'Lesser-known tests', b'quality',
         b'20181225112233', b'Stub-Class', b'Start-Class',
         b'2018-12-25T08:22:33Z'),
        (b'Catholicism', 0, b'Operation of tests', b'importance',
         b'20181227130000', b'Unassessed-Class', b'Mid-Class',
         b'2018-12-27T08:00:00Z'),
        (b'Catholicism', 0, b'Operation of tests', b'quality',
         b'20181227130000', b'B-Class', b'Unassessed-Class',
         b'2018-12-27T08:00:00Z'),
        (b'Catholicism', 0, b'Rules of testing', b'quality', b'20181227130000',
         b'B-Class', b'FA-Class', b'2018-12-27T08:00:00Z'),
        (b'Catholicism', 0, b'Test Baz Bang', b'moved', b'20181225112233', None,
         None, b'2018-12-25T08:22:33Z'),
        (b'Catholicism', 0, b'Test Foo Bar', b'moved', b'20181227130000', None,
         None, b'2018-12-27T08:00:00Z'),
        (b'Catholicism', 0, b'Test for None-abc', b'importance',
         b'20181227130000', None, b'Unknown-Class', b'2018-12-27T08:00:00Z'),
        (b'Catholicism', 0, b'Test frameworks', b'quality', b'20181226101010',
         b'NotA-Class', b'FL-Class', b'2018-12-26T05:10:10Z'),
        (b'Catholicism', 0, b'Test main inheritance', b'importance',
         b'20181226101010', b'NotA-Class', b'NotA-Class',
         b'2018-12-26T05:10:10Z'),
        (b'Catholicism', 0, b'Test main inheritance', b'quality',
         b'20181226101010', b'NotA-Class', b'NotA-Class',
         b'2018-12-26T05:10:10Z'),
        (b'Catholicism', 0, b'Test other inheritance', b'quality',
         b'20181225112233', b'Unknown-Class', b'B-Class',
         b'2018-12-25T08:22:33Z'),
        (b'Catholicism', 0, b'Test results', b'importance', b'20181227130000',
         b'NotA-Class', b'Mid-Class', b'2018-12-27T08:00:00Z'),
        (b'Catholicism', 0, b'Test results', b'quality', b'20181227130000',
         b'GA-Class', b'NotA-Class', b'2018-12-27T08:00:00Z'),
        (b'Catholicism', 0, b'Test sub inheritance', b'quality',
         b'20181227130000', b'Unknown-Class', b'GA-Class',
         b'2018-12-27T08:00:00Z'),
        (b'Catholicism', 0, b'Testing None-a', b'importance', b'20181225112233',
         None, None, b'2018-12-25T08:22:33Z'),
        (b'Catholicism', 0, b'Testing None-ab', b'importance',
         b'20181226101010', b'Stub-Class', None, b'2018-12-26T05:10:10Z'),
        (b'Catholicism', 0, b'Testing best practices', b'quality',
         b'20181226101010', b'C-Class', b'B-Class', b'2018-12-26T05:10:10Z'),
        (b'Catholicism', 0, b'Testing figures', b'importance',
         b'20181227130000', b'A-Class', b'NotA-Class', b'2018-12-27T08:00:00Z'),
        (b'Catholicism', 0, b'Testing figures', b'quality', b'20181227130000',
         b'NotA-Class', b'A-Class', b'2018-12-27T08:00:00Z'),
        (b'Catholicism', 0, b'Testing history', b'quality', b'20181225112233',
         b'Unassessed-Class', b'FL-Class', b'2018-12-25T08:22:33Z'),
        (b'Catholicism', 0, b'Testing in Copenhaven', b'moved',
         b'20181225112233', None, None, b'2018-12-25T08:22:33Z'),
        (b'Catholicism', 0, b'Testing tools', b'quality', b'20181225112233',
         b'B-Class', b'NotA-Class', b'2018-12-25T08:22:33Z'),
        (b'Catholicism', 0, b'Tests', b'moved', b'20181226101010', None, None,
         b'2018-12-26T05:10:10Z'),
        (b'Catholicism', 14, b'Test practices', b'quality', b'20181225112233',
         b'Unknown-Class', b'Category-Class', b'2018-12-25T08:22:33Z'),
        (b'Catholicism', 14, b'Testing mechanics', b'quality',
         b'20181226101010', b'NotA-Class', b'Category-Class',
         b'2018-12-26T05:10:10Z')
    ]
    actual = logs.get_logs(self.wp10db, self.project, datetime(2018, 11, 24))
    actual = list(attr.astuple(a) for a in actual)
    self.assertEqual(sorted(expected), sorted(actual))

  def test_move_target(self):
    for i, m in enumerate(self.moves):
      actual = logs.move_target(
          self.wp10db, 0, m[0],
          self.wiki_timestamps[i % len(self.wiki_timestamps)])
      self.assertEqual(0, actual['ns'])
      self.assertEqual(m[1], actual['article'])

  def test_get_revid_nonexistant_page(self):
    actual = logs.get_revid(self.wikidb, b'Non-existant', 0,
                            datetime(2018, 1, 1))
    self.assertIsNone(actual)

  def test_get_revid(self):
    for l in self._logs():
      if l.l_action == b'moved':
        continue
      actual = logs.get_revid(self.wikidb, l.l_article, l.l_namespace,
                              l.rev_timestamp_dt)
      self.assertEqual(int('%s000' % len(l.l_article)), actual, l)

  def test_name_for_article_normal(self):
    actual = logs.name_for_article(self.wp10db, b'Test Article', 0)
    self.assertEqual('Test Article', actual)

  def test_name_for_article_category(self):
    actual = logs.name_for_article(self.wp10db, b'Test Category', 14)
    self.assertEqual(':Category:Test Category', actual)

  def test_talk_page_for_article_normal(self):
    actual = logs.talk_page_for_article(self.wp10db, b'Test Article', 0)
    self.assertEqual('Talk:Test Article', actual)

  def test_talk_page_for_article_category(self):
    actual = logs.talk_page_for_article(self.wp10db, b'Test Category', 14)
    self.assertEqual('Category talk:Test Category', actual)

  @patch('wp1.logs.get_current_datetime',
         return_value=datetime(2018, 12, 28, 12))
  def test_calculate_logs_to_update_keys(self, patched_datetime_now):
    actual = logs.calculate_logs_to_update(self.wikidb, self.wp10db,
                                           self.project)
    self.assertEqual(3, len(actual))
    self.assertTrue(datetime(2018, 12, 25).date() in actual)
    self.assertTrue(datetime(2018, 12, 26).date() in actual)
    self.assertTrue(datetime(2018, 12, 27).date() in actual)

  @patch('wp1.logs.get_current_datetime',
         return_value=datetime(2018, 12, 28, 12))
  def test_calculate_logs_to_update_values(self, patched_current_datetime):
    expected = [
        l for l in self._logs()
        if l.l_revision_timestamp.startswith(b'2018-12-25')
    ]
    expected.extend(l for l in self._move_logs()
                    if l.l_revision_timestamp.startswith(b'2018-12-25'))
    actual = logs.calculate_logs_to_update(self.wikidb, self.wp10db,
                                           self.project)

    for d in ((25, b'2018-12-25'), (26, b'2018-12-26'), (27, b'2018-12-27')):
      expected = [
          l for l in self._logs() if l.l_revision_timestamp.startswith(d[1])
      ]
      expected.extend(l for l in self._move_logs()
                      if l.l_revision_timestamp.startswith(d[1]))
      self.assertEqual(sorted(expected),
                       sorted(actual[datetime(2018, 12, d[0]).date()]))

  def test_get_section_categories(self):
    expected = {
        'assessed': {
            b'Testing mechanics', b'Test frameworks', b'Important tests'
        },
        'reassessed': {
            b'Art of testing', b'Failures of tests', b'How to test',
            b'Lesser-known tests', b'Operation of tests', b'Rules of testing',
            b'Test for None-abc', b'Test other inheritance', b'Test practices',
            b'Test results', b'Test sub inheritance', b'Testing best practices',
            b'Testing figures', b'Testing history'
        },
        'removed': {
            b'Test main inheritance', b'Testing None-a', b'Testing None-ab',
            b'Testing tools'
        },
        'renamed': set()
    }
    l = defaultdict(defaultdict)
    for log in self._logs():
      l[log.l_article][log.l_action.decode('utf-8')] = log

    actual = logs.get_section_categories(l)
    self.assertEqual(expected, actual)

  def test_get_section_data(self):
    expected = {
        'log_date': 'December 25, 2018',
        'moved_name': {
            b'Test Baz Bang': 'Test Baz',
            b'Testing in Copenhaven': 'Testing in Copenhagen'
        },
        'name': {
            b'Important tests': 'Important tests',
            b'Lesser-known tests': 'Lesser-known tests',
            b'Test Baz Bang': 'Test Baz Bang',
            b'Test other inheritance': 'Test other inheritance',
            b'Test practices': ':Category:Test practices',
            b'Testing None-a': 'Testing None-a',
            b'Testing history': 'Testing history',
            b'Testing in Copenhaven': 'Testing in Copenhaven',
            b'Testing tools': 'Testing tools'
        },
        'revid': {
            b'Important tests': {
                'importance': 15000,
                'quality': 15000
            },
            b'Lesser-known tests': {
                'importance': 18000,
                'quality': 18000
            },
            b'Test other inheritance': {
                'quality': 22000
            },
            b'Test practices': {
                'quality': 14000
            },
            b'Testing None-a': {
                'importance': 14000
            },
            b'Testing history': {
                'quality': 15000
            },
            b'Testing tools': {
                'quality': 13000
            }
        },
        'talk': {
            b'Important tests': 'Talk:Important tests',
            b'Lesser-known tests': 'Talk:Lesser-known tests',
            b'Test Baz Bang': 'Talk:Test Baz Bang',
            b'Test other inheritance': 'Talk:Test other inheritance',
            b'Test practices': 'Category talk:Test practices',
            b'Testing None-a': 'Talk:Testing None-a',
            b'Testing history': 'Talk:Testing history',
            b'Testing in Copenhaven': 'Talk:Testing in Copenhaven',
            b'Testing tools': 'Talk:Testing tools'
        },
        'talk_revid': {
            b'Important tests': {
                'importance': None,
                'quality': None
            },
            b'Lesser-known tests': {
                'importance': None,
                'quality': None
            },
            b'Test other inheritance': {
                'quality': None
            },
            b'Test practices': {
                'quality': None
            },
            b'Testing None-a': {
                'importance': None
            },
            b'Testing history': {
                'quality': None
            },
            b'Testing tools': {
                'quality': None
            }
        }
    }
    test_logs = [
        l for l in self._logs()
        if l.l_revision_timestamp.startswith(b'2018-12-25')
    ]
    test_logs.extend(l for l in self._move_logs()
                     if l.l_revision_timestamp.startswith(b'2018-12-25'))
    expected_l = defaultdict(defaultdict)
    for log in test_logs:
      expected_l[log.l_article][log.l_action.decode('utf-8')] = log

    actual = logs.get_section_data(self.wikidb, self.wp10db, b'Catholicism',
                                   datetime(2018, 12, 25).date(), test_logs)

    # Clean up the actual so we can compare them.
    actual_test = dict(actual)
    for k, v in actual.items():
      if isinstance(v, defaultdict):
        actual_test[k] = dict(v)
    for sub in ('revid', 'talk_revid'):
      for k, v in actual[sub].items():
        actual_test[sub][k] = dict(v)

    # These are tested in test_get_section_data
    del actual_test['assessed']
    del actual_test['reassessed']
    del actual_test['renamed']
    del actual_test['removed']

    self.assertEqual(expected_l, actual_test['l'])
    del actual_test['l']
    self.assertEqual(expected, actual_test)

  def test_section_for_date(self):
    # Excuse my mess.
    expected = ('=== December 25, 2018 ===\n'
                '==== Renamed ====\n'
                "* '''[[Test Baz Bang]]''' renamed to '''[[Test Baz]]'''.\n"
                "* '''[[Testing in Copenhaven]]''' renamed to '''[[Testing in "
                "Copenhagen]]'''.\n"
                '==== Reassessed ====\n'
                "* '''[[Lesser-known tests]]''' ([[Talk:Lesser-known "
                'tests|talk]]) reassessed.  Quality rating changed from '
                "'''Stub-Class''' to '''Start-Class'''. <span "
                'style=\\"white-space: '
                'nowrap;\\">([https://en.wikipedia.org/w/index.php?'
                'title=Lesser-known%20tests&oldid=18000 '
                'rev] &middot; '
                '[https://en.wikipedia.org/w/index.php?'
                'title=Talk%3ALesser-known%20tests&oldid=None '
                "t])</span> Importance rating changed from '''Start-Class''' "
                'to \'\'\'Unknown-Class\'\'\'. <span style=\\"white-space: '
                'nowrap;\\">([https://en.wikipedia.org/w/index.php?'
                'title=Lesser-known%20tests&oldid=18000 '
                'rev] &middot; '
                '[https://en.wikipedia.org/w/index.php?'
                'title=Talk%3ALesser-known%20tests&oldid=None '
                't])</span>\n'
                "* '''[[Test other inheritance]]''' ([[Talk:Test other "
                'inheritance|talk]]) reassessed.  Quality rating changed from '
                "'''Unknown-Class''' to '''B-Class'''. <span "
                'style=\\"white-space: '
                'nowrap;\\">([https://en.wikipedia.org/w/index.php?'
                'title=Test%20other%20inheritance&oldid=22000 '
                'rev] &middot; '
                '[https://en.wikipedia.org/w/index.php?'
                'title=Talk%3ATest%20other%20inheritance&oldid=None '
                't])</span>\n'
                "* '''[[:Category:Test practices]]''' ([[Category talk:Test "
                'practices|talk]]) reassessed.  Quality rating changed from '
                "'''Unknown-Class''' to '''Category-Class'''. <span "
                'style=\\"white-space: '
                'nowrap;\\">([https://en.wikipedia.org/w/index.php?'
                'title=%3ACategory%3ATest%20practices&oldid=14000 '
                'rev] &middot; '
                '[https://en.wikipedia.org/w/index.php?'
                'title=Category%20talk%3ATest%20practices&oldid=None '
                't])</span>\n'
                "* '''[[Testing history]]''' ([[Talk:Testing history|talk]]) "
                'reassessed.  Quality rating changed from '
                "'''Unassessed-Class''' to '''FL-Class'''. <span "
                'style=\\"white-space: '
                'nowrap;\\">([https://en.wikipedia.org/w/index.php?'
                'title=Testing%20history&oldid=15000 '
                'rev] &middot; '
                '[https://en.wikipedia.org/w/index.php?'
                'title=Talk%3ATesting%20history&oldid=None '
                't])</span>\n'
                '\n'
                '==== Assessed ====\n'
                "* '''[[Important tests]]''' ([[Talk:Important tests|talk]]) "
                "assessed.  Quality assessed as '''NotA-Class'''. <span "
                'style=\\"white-space: '
                'nowrap;\\">([https://en.wikipedia.org/w/index.php?'
                'title=Important%20tests&oldid=15000 '
                'rev] &middot; '
                '[https://en.wikipedia.org/w/index.php?'
                'title=Talk%3AImportant%20tests&oldid=None '
                "t])</span> Importance assessed as '''Unknown-Class'''. <span "
                'style=\\"white-space: '
                'nowrap;\\">([https://en.wikipedia.org/w/index.php?'
                'title=Important%20tests&oldid=15000 '
                'rev] &middot; '
                '[https://en.wikipedia.org/w/index.php?'
                'title=Talk%3AImportant%20tests&oldid=None '
                't])</span>\n'
                '\n'
                '==== Removed ====\n'
                "* '''[[Testing None-a]]''' ([[Talk:Testing None-a|talk]]) "
                'removed. \n'
                "* '''[[Testing tools]]''' ([[Talk:Testing tools|talk]]) "
                'removed. \n')

    test_logs = [
        l for l in self._logs()
        if l.l_revision_timestamp.startswith(b'2018-12-25')
    ]
    test_logs.extend(l for l in self._move_logs()
                     if l.l_revision_timestamp.startswith(b'2018-12-25'))

    actual = logs.section_for_date(self.wikidb, self.wp10db, b'Catholicism',
                                   datetime(2018, 12, 25).date(), test_logs)
    self.assertEqual(expected, actual)

  def test_generate_log_edits(self):
    log_map = {}
    dates = ((25, b'2018-12-25'), (26, b'2018-12-26'), (27, b'2018-12-27'))
    for num, s in dates:
      test_logs = [
          l for l in self._logs() if l.l_revision_timestamp.startswith(s)
      ]
      test_logs.extend(
          l for l in self._move_logs() if l.l_revision_timestamp.startswith(s))
      log_map[datetime(2018, 12, num).date()] = test_logs

    actual = logs.generate_log_edits(self.wikidb, self.wp10db, b'Catholicism',
                                     log_map)

    self.assertEqual(3, len(actual))
    self.assertTrue(actual[0].startswith('=== December 27, 2018 ==='))
    self.assertTrue(actual[1].startswith('=== December 26, 2018 ==='))
    self.assertTrue(actual[2].startswith('=== December 25, 2018 ==='))

  @patch('wp1.logs.wiki_connect')
  @patch('wp1.logs.wp10_connect')
  @patch('wp1.logs.api')
  def test_upload_log_page_for_project(self, patched_api, patched_wp10,
                                       patched_wiki):
    logs.update_log_page_for_project(b'Catholicism')
    call = patched_api.save_page.call_args[0]
    self.assertEqual('Update logs for past 7 days', call[2])

  @patch('wp1.logs.wiki_connect')
  @patch('wp1.logs.wp10_connect')
  @patch('wp1.logs.api')
  @patch('wp1.logs.get_current_datetime',
         return_value=datetime(2018, 12, 28, 12))
  def test_upload_log_page_for_project_no_logs(self, patched_datetime,
                                               patched_api, patched_wp10,
                                               patched_wiki):
    project_name = b'Catholicism'
    header = '<noinclude>{{Log}}</noinclude>\n'
    no_logs_msg = ("'''There were no logs for this project from December 21, "
                   "2018 - December 28, 2018.'''")
    logs.update_log_page_for_project(project_name)
    call = patched_api.save_page.call_args[0]
    self.assertEqual(header + no_logs_msg, call[1])

  @patch('wp1.logs.wiki_connect')
  @patch('wp1.logs.wp10_connect')
  @patch('wp1.logs.api')
  @patch('wp1.logs.generate_log_edits')
  def test_upload_log_page_for_project_huge_text(self, patched_generate,
                                                 patched_api, patched_wp10,
                                                 patched_wiki):
    project_name = b'Catholicism'
    header = '<noinclude>{{Log}}</noinclude>\n'
    text = 'a' * 1000 * 1024
    patched_generate.return_value = [text, text, text]
    logs.update_log_page_for_project(project_name)
    call = patched_api.save_page.call_args[0]
    self.assertEqual('%s%s\n%s' % (header, text, text), call[1])

  @patch('wp1.logs.wiki_connect')
  @patch('wp1.logs.wp10_connect')
  @patch('wp1.logs.api')
  @patch('wp1.logs.generate_log_edits')
  def test_upload_log_page_for_project_huge_give_up(self, patched_generate,
                                                    patched_api, patched_wp10,
                                                    patched_wiki):
    project_name = b'Catholicism'
    sorry_msg = ('Sorry, all of the logs for this date were too large to '
                 'upload.')
    header = '<noinclude>{{Log}}</noinclude>\n'
    text = 'a' * 3000 * 1024
    patched_generate.return_value = [text, text, text]
    logs.update_log_page_for_project(b'Catholicism')
    call = patched_api.save_page.call_args[0]
    self.assertEqual(header + sorry_msg, call[1])
