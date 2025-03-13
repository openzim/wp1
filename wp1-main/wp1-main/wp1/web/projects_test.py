from datetime import datetime
import json
from unittest.mock import patch

from wp1.logic import project as logic_project
from wp1.web.app import create_app
from wp1.web.base_web_testcase import BaseWebTestcase
from wp1.environment import Environment


class ProjectTest(BaseWebTestcase):
  USER = {
      'access_token': 'access_token',
      'identity': {
          'username': 'WP1_user',
          'sub': '1234'
      }
  }
  EXPECTED_CATEGORY_LINKS = {
      'A-Class': {
          'href':
              'https://en.wikipedia.org/wiki/Category:A-Class_Project_0_articles',
          'text':
              'A'
      },
      'Assessed-Class': 'Assessed',
      'B-Class': {
          'href':
              'https://en.wikipedia.org/wiki/Category:B-Class_Project_0_articles',
          'text':
              'B'
      },
      'FA-Class': {
          'href':
              'https://en.wikipedia.org/wiki/Category:FA-Class_Project_0_articles',
          'text':
              'FA'
      },
      'High-Class': {
          'href':
              'https://en.wikipedia.org/wiki/Category:High-Class_Project_0_articles',
          'text':
              'High'
      },
      'Low-Class': {
          'href':
              'https://en.wikipedia.org/wiki/Category:Low-Class_Project_0_articles',
          'text':
              'Low'
      },
      'Unassessed-Class': "'''Unassessed'''",
  }
  EXPECTED_CATEGORY_LINKS_SORTED = {
      'quality': {
          'A-Class': {
              'href':
                  'https://en.wikipedia.org/wiki/Category:A-Class_Project_0_articles',
              'text':
                  'A'
          },
          'Assessed-Class': 'Assessed',
          'B-Class': {
              'href':
                  'https://en.wikipedia.org/wiki/Category:B-Class_Project_0_articles',
              'text':
                  'B'
          },
          'FA-Class': {
              'href':
                  'https://en.wikipedia.org/wiki/Category:FA-Class_Project_0_articles',
              'text':
                  'FA'
          },
          'Unassessed-Class': "'''Unassessed'''",
      },
      'importance': {
          'High-Class': {
              'href':
                  'https://en.wikipedia.org/wiki/Category:High-Class_Project_0_articles',
              'text':
                  'High'
          },
          'Low-Class': {
              'href':
                  'https://en.wikipedia.org/wiki/Category:Low-Class_Project_0_articles',
              'text':
                  'Low'
          },
          'Unassessed-Class': 'No-Class',
      }
  }

  def setUp(self):
    super().setUp()
    projects = []
    for i in range(101):
      projects.append({
          'p_project': b'Project %s' % str(i).encode('utf-8'),
          'p_timestamp': b'20181225'
      })

    ratings = []
    categories = set()
    for i in range(25):
      for quality in ('FA-Class', 'A-Class', 'B-Class'):
        categories.add(('Project 0', 'quality', quality, quality,
                        '%s_Project_0_articles' % quality, 100))
        for importance in ('High-Class', 'Low-Class'):
          categories.add(('Project 0', 'importance', importance, importance,
                          '%s_Project_0_articles' % importance, 100))
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
          ratings.append({
              'r_project': 'Project 1',
              'r_namespace': 0,
              'r_article': '%s_%s_%s' % (quality, importance, i),
              'r_score': 0,
              'r_quality': quality,
              'r_quality_timestamp': '20191225T00:00:00',
              'r_importance': importance,
              'r_importance_timestamp': '20191226T00:00:00',
          })

    with self.wp10db.cursor() as cursor:
      cursor.executemany(
          'INSERT INTO projects (p_project, p_timestamp) '
          'VALUES (%(p_project)s, %(p_timestamp)s)', projects)
      cursor.executemany(
          'INSERT INTO ratings '
          '(r_project, r_namespace, r_article, r_score, r_quality, '
          ' r_quality_timestamp, r_importance, r_importance_timestamp) '
          'VALUES '
          '(%(r_project)s, %(r_namespace)s, %(r_article)s, %(r_score)s, '
          ' %(r_quality)s, %(r_quality_timestamp)s, %(r_importance)s, '
          ' %(r_importance_timestamp)s)', ratings)
      cursor.executemany(
          'INSERT INTO categories VALUES (%s, %s, %s, %s, %s, %s)',
          list(categories))
    self.wp10db.commit()

  def test_list(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/')
      data = json.loads(rv.data)
      self.assertEqual(101, len(data))

  def test_individual_project(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Project 0')
      self.assertEqual('200 OK', rv.status)

      data = json.loads(rv.data)
      self.assertEqual(2, len(data))

  def test_individual_project_404(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Fee Fa Fo Project')
      self.assertEqual('404 NOT FOUND', rv.status)

  def test_count(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/count')
      data = json.loads(rv.data)
      self.assertEqual(101, data['count'])

  def test_table(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Project 1/table')
      data = json.loads(rv.data)
      self.assertTrue('data' in data['table_data'])

  def test_table_404(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Foo Fake Project/table')
      self.assertEqual('404 NOT FOUND', rv.status)

  def test_articles_ok(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Project 0/articles')
      self.assertEqual('200 OK', rv.status)

  def test_articles_returned(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Project 0/articles')
      data = json.loads(rv.data)

      # Currently limited to 100 items
      self.assertEqual(100, len(data['articles']))

  def test_articles_quality_only(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Project 0/articles?quality=FA-Class')
      data = json.loads(rv.data)

      # Currently limited to 100 items
      self.assertEqual(50, len(data['articles']))
      for article in data['articles']:
        self.assertEqual('FA-Class', article['quality'])

  def test_articles_importance_only(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Project 0/articles?importance=High-Class')
      data = json.loads(rv.data)

      self.assertEqual(75, len(data['articles']))
      for article in data['articles']:
        self.assertEqual('High-Class', article['importance'])

  def test_articles_quality_importance(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get(
          '/v1/projects/Project 0/articles?quality=A-Class&importance=Low-Class'
      )
      data = json.loads(rv.data)

      self.assertEqual(25, len(data['articles']))
      for article in data['articles']:
        self.assertEqual('Low-Class', article['importance'])
        self.assertEqual('A-Class', article['quality'])

  def test_articles_no_results(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get(
          '/v1/projects/Project 0/articles?quality=Foo-Bar&importance=Low-Class'
      )
      self.assertEqual('200 OK', rv.status)
      data = json.loads(rv.data)
      self.assertEqual(0, len(data['articles']))

  def test_articles_pagination(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Project 0/articles')
      self.assertEqual('200 OK', rv.status)
      data = json.loads(rv.data)

      self.assertEqual(1, data['pagination']['page'])
      self.assertEqual(150, data['pagination']['total'])
      self.assertEqual(2, data['pagination']['total_pages'])

  def test_articles_page_2(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Project 0/articles?page=2')
      self.assertEqual('200 OK', rv.status)
      data = json.loads(rv.data)
      self.assertEqual(50, len(data['articles']))

  def test_articles_num_rows(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Project 0/articles?page=2&numRows=25')
      self.assertEqual('200 OK', rv.status)
      data = json.loads(rv.data)
      self.assertEqual(25, len(data['articles']))

  def test_articles_404(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Foo Fake Project/articles')
      self.assertEqual('404 NOT FOUND', rv.status)

  def test_articles_400_invalid_page(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Project 0/articles?page=foo')
      self.assertEqual('400 BAD REQUEST', rv.status)

    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Project 0/articles?page=-5')
      self.assertEqual('400 BAD REQUEST', rv.status)

  def test_articles_404_project_b(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Project 0/articles?projectB=Foo')
      self.assertEqual('404 NOT FOUND', rv.status)

  def test_articles_project_b(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Project 0/articles?projectB=Project 1')
      self.assertEqual('200 OK', rv.status)

  def test_articles_project_b_quality_left(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get(
          '/v1/projects/Project 0/articles?quality=A-Class&projectB=Project 1')
      self.assertEqual('200 OK', rv.status)

  def test_articles_project_b_quality_right(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get(
          '/v1/projects/Project 0/articles?qualityB=A-Class&projectB=Project 1')
      self.assertEqual('200 OK', rv.status)

  def test_articles_project_b_quality_both(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get(
          '/v1/projects/Project 0/articles?quality=A-Class&qualityB=A-Class&projectB=Project 1'
      )
      self.assertEqual('200 OK', rv.status)

  def test_articles_project_b_importance_left(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get(
          '/v1/projects/Project 0/articles?importance=A-Class&projectB=Project 1'
      )
      self.assertEqual('200 OK', rv.status)

  def test_articles_project_b_importance_right(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get(
          '/v1/projects/Project 0/articles?importanceB=A-Class&projectB=Project 1'
      )
      self.assertEqual('200 OK', rv.status)

  def test_articles_project_b_importance_both(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get(
          '/v1/projects/Project 0/articles?importance=A-Class&importanceB=A-Class&projectB=Project 1'
      )
      self.assertEqual('200 OK', rv.status)

  @patch('wp1.queues.ENV', Environment.PRODUCTION)
  @patch('wp1.queues.utcnow', return_value=datetime(2018, 12, 25, 5, 55, 55))
  def test_update(self, patched_now):
    with self.override_db(self.app), self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/projects/Project 0/update')
      self.assertEqual('200 OK', rv.status)

      data = json.loads(rv.data)
      self.assertEqual('2018-12-25 06:55 UTC', data['next_update_time'])

  @patch('wp1.queues.ENV', Environment.PRODUCTION)
  def test_update_unauthorized_user(self):
    with self.app.test_client() as client:
      rv = client.post('/v1/projects/Project 0/update')
    self.assertEqual('401 UNAUTHORIZED', rv.status)

  @patch('wp1.queues.ENV', Environment.PRODUCTION)
  @patch('wp1.queues.utcnow', return_value=datetime(2018, 12, 25, 5, 55, 55))
  def test_update_404(self, patched_now):
    with self.override_db(self.app), self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/projects/Foo Bar Baz/update')
      self.assertEqual('404 NOT FOUND', rv.status)

  @patch('wp1.queues.ENV', Environment.PRODUCTION)
  @patch('wp1.queues.utcnow', return_value=datetime(2018, 12, 25, 5, 55, 55))
  def test_update_second_time_fails(self, patched_now):
    with self.override_db(self.app):
      with self.app.test_client() as client:
        with client.session_transaction() as sess:
          sess['user'] = self.USER
        rv = client.post('/v1/projects/Project 0/update')
        self.assertEqual('200 OK', rv.status)

        data = json.loads(rv.data)
        self.assertEqual('2018-12-25 06:55 UTC', data['next_update_time'])

        rv = client.post('/v1/projects/Project 0/update')
        self.assertEqual('400 BAD REQUEST', rv.status)

        data = json.loads(rv.data)
        self.assertEqual('2018-12-25 06:55 UTC', data['next_update_time'])

  @patch('wp1.queues.ENV', Environment.PRODUCTION)
  @patch('wp1.queues.utcnow', return_value=datetime(2018, 12, 25, 5, 55, 55))
  def test_update_time(self, patched_now):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Project 0/update/time')
      self.assertEqual('200 OK', rv.status)

      data = json.loads(rv.data)
      self.assertEqual(None, data['next_update_time'])

  @patch('wp1.queues.ENV', Environment.PRODUCTION)
  @patch('wp1.queues.utcnow', return_value=datetime(2018, 12, 25, 5, 55, 55))
  def test_update_time_404(self, patched_now):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Foo Bar Baz/update/time')
      self.assertEqual('404 NOT FOUND', rv.status)

  @patch('wp1.queues.ENV', Environment.PRODUCTION)
  @patch('wp1.queues.utcnow', return_value=datetime(2018, 12, 25, 5, 55, 55))
  def test_update_time_active(self, patched_now):
    with self.override_db(self.app):
      with self.app.test_client() as client:
        with client.session_transaction() as sess:
          sess['user'] = self.USER
        rv = client.post('/v1/projects/Project 0/update')
        self.assertEqual('200 OK', rv.status)

        data = json.loads(rv.data)
        self.assertEqual('2018-12-25 06:55 UTC', data['next_update_time'])

        rv = client.get('/v1/projects/Project 0/update/time')
        self.assertEqual('200 OK', rv.status)

        data = json.loads(rv.data)
        self.assertEqual('2018-12-25 06:55 UTC', data['next_update_time'])

  def test_update_progress_empty(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Project 0/update/progress')
      self.assertEqual('200 OK', rv.status)

      data = json.loads(rv.data)
      self.assertIsNone(data['queue'])
      self.assertIsNone(data['job'])

  @patch('wp1.queues.ENV', Environment.PRODUCTION)
  def test_update_progress(self):
    with self.override_db(self.app), self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.post('/v1/projects/Project 0/update')
      self.assertEqual('200 OK', rv.status)

      rv = client.get('/v1/projects/Project 0/update/progress')
      self.assertEqual('200 OK', rv.status)

      data = json.loads(rv.data)
      self.assertIsNone(data['job'])
      self.assertEqual({'status': 'queued'}, data['queue'])

  @patch('wp1.queues.ENV', Environment.PRODUCTION)
  def test_update_progress_404(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Foo Bar Baz/update/progress')
      self.assertEqual('404 NOT FOUND', rv.status)

  @patch('wp1.queues.ENV', Environment.PRODUCTION)
  def test_update_progress_return_job_progress(self):
    with self.override_db(self.app), self.app.test_client() as client:
      expected_total = 100
      expected_progress = 25

      key = logic_project._project_progress_key(b'Project 0')
      self.redis.hset(key, 'work', expected_total)
      self.redis.hset(key, 'progress', expected_progress)

      rv = client.get('/v1/projects/Project 0/update/progress')
      self.assertEqual('200 OK', rv.status)

      data = json.loads(rv.data)
      self.assertEqual(expected_total, data['job']['total'])
      self.assertEqual(expected_progress, data['job']['progress'])

  @patch('wp1.queues.ENV', Environment.PRODUCTION)
  @patch('wp1.web.projects.logic_project.get_project_progress')
  def test_update_progress_progress_not_ints(self, patched_progress):
    patched_progress.return_value = (b'a', b'b')

    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Project 0/update/progress')
      self.assertEqual('200 OK', rv.status)

      data = json.loads(rv.data)
      self.assertEqual(0, data['job']['progress'])
      self.assertEqual(0, data['job']['total'])

  def test_category_links(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Project 0/category_links')
      self.assertEqual('200 OK', rv.status)

      data = json.loads(rv.data)
      self.assertEqual(self.EXPECTED_CATEGORY_LINKS, data)

  def test_category_links_404(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Foo Bar Baz/category_links')
      self.assertEqual('404 NOT FOUND', rv.status)

  def test_category_links_sorted(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Project 0/category_links/sorted')
      self.assertEqual('200 OK', rv.status)

      data = json.loads(rv.data)
      self.assertEqual(self.EXPECTED_CATEGORY_LINKS_SORTED, data)

  def test_category_links_sorted_404(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/Foo Bar Baz/category_links/sorted')
      self.assertEqual('404 NOT FOUND', rv.status)
