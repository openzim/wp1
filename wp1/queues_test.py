import unittest
from unittest.mock import patch, MagicMock

import fakeredis

from wp1.base_db_test import BaseWpOneDbTest
from wp1 import constants
from wp1.environment import Environment
from wp1 import queues
from wp1.selection.models.simple import Builder as SimpleBuilder


class QueuesTest(BaseWpOneDbTest):

  def setUp(self):
    super().setUp()
    self.redis = fakeredis.FakeStrictRedis()

  def tearDown(self):
    super().tearDown()
    self.redis = None

  @patch('wp1.queues.ENV', Environment.DEVELOPMENT)
  @patch('wp1.queues.logic_project.update_project_by_name')
  def test_enqueue_project_development(self, patched_project_fn):
    update_q = MagicMock()
    upload_q = MagicMock()

    queues.enqueue_project(b'Water', update_q, upload_q)

    update_q.enqueue.assert_called_once_with(
        patched_project_fn,
        b'Water',
        job_timeout=constants.JOB_TIMEOUT,
        failure_ttl=constants.JOB_FAILURE_TTL,
        track_progress=False)
    upload_q.enqueue.assert_not_called()

  @patch('wp1.queues.ENV', Environment.PRODUCTION)
  @patch('wp1.queues.logic_project.update_project_by_name')
  @patch('wp1.queues.tables.upload_project_table')
  @patch('wp1.queues.logs.update_log_page_for_project')
  def test_enqueue_project_production(self, patched_log_fn, patched_tables_fn,
                                      patched_project_fn):
    update_q = MagicMock()
    upload_q = MagicMock()
    update_job = MagicMock()
    update_job.id = '1234-567'
    update_q.enqueue.return_value = update_job
    project_name = b'Water'

    queues.enqueue_project(project_name, update_q, upload_q)

    update_q.enqueue.assert_called_once_with(
        patched_project_fn,
        project_name,
        job_timeout=constants.JOB_TIMEOUT,
        failure_ttl=constants.JOB_FAILURE_TTL,
        track_progress=False)
    upload_q.enqueue.assert_any_call(patched_tables_fn,
                                     project_name,
                                     depends_on=update_job,
                                     job_timeout=constants.JOB_TIMEOUT,
                                     failure_ttl=constants.JOB_FAILURE_TTL)
    upload_q.enqueue.assert_any_call(patched_log_fn,
                                     project_name,
                                     depends_on=update_job,
                                     job_timeout=constants.JOB_TIMEOUT,
                                     failure_ttl=constants.JOB_FAILURE_TTL)

  @patch('wp1.queues.ENV', Environment.DEVELOPMENT)
  @patch('wp1.queues.Queue')
  @patch('wp1.queues.enqueue_project')
  def test_enqueue_single_project(self, patched_enqueue_project, patched_queue):
    update_q = MagicMock()
    upload_q = MagicMock

    patched_queue.side_effect = lambda name, connection=None: update_q if name == 'update' else upload_q

    queues.enqueue_single_project(self.redis, b'Water')

    patched_enqueue_project.assert_called_once_with(b'Water',
                                                    update_q,
                                                    upload_q,
                                                    redis=self.redis,
                                                    track_progress=False)

  @patch('wp1.queues.ENV', Environment.DEVELOPMENT)
  @patch('wp1.queues.custom_tables.upload_custom_table_by_name')
  @patch('wp1.queues.Queue')
  @patch('wp1.queues.enqueue_project')
  def test_enqueue_multipe_projects(self, patched_enqueue_project,
                                    patched_queue, patched_upload):
    projects = (b'Water', b'Air', b'Fire', b'Earth')
    update_q = MagicMock()
    upload_q = MagicMock()
    patched_queue.side_effect = lambda name, connection=None: update_q if name == 'update' else upload_q

    queues.enqueue_custom_table(self.redis, b'Water')

    upload_q.enqueue.assert_any_call(patched_upload,
                                     b'Water',
                                     job_timeout=constants.JOB_TIMEOUT,
                                     failure_ttl=constants.JOB_FAILURE_TTL)

  @patch('wp1.queues.ENV', Environment.DEVELOPMENT)
  @patch('wp1.queues.logic_project.project_names_to_update')
  @patch('wp1.queues.custom_tables.all_custom_table_names')
  @patch('wp1.queues.wiki_connect')
  @patch('wp1.queues.Queue')
  @patch('wp1.queues.enqueue_project')
  @patch('wp1.queues.enqueue_custom_table')
  def test_enqueue_all(self, patched_enqueue_custom, patched_enqueue_project,
                       patched_queue, patched_db_connect, patched_custom_names,
                       patched_names):
    projects = (b'Water', b'Air', b'Fire', b'Earth')
    patched_names.return_value = projects
    custom_names = (b'North', b'South', b'East', b'West')
    patched_custom_names.return_value = custom_names

    update_q = MagicMock()
    upload_q = MagicMock()
    update_q.count = 0
    upload_q.count = 0

    patched_queue.side_effect = lambda name, connection=None: update_q if name == 'update' else upload_q

    queues.enqueue_all_projects(self.redis, self.wp10db)

    for project_name in projects:
      patched_enqueue_project.assert_any_call(project_name, update_q, upload_q)

    for name in custom_names:
      patched_enqueue_custom.assert_any_call(self.redis, name)

  def test_next_update_time_empty(self):
    actual = queues.next_update_time(self.redis, b'Some_Project')
    self.assertIsNone(actual)

  def test_next_update_time_after_update(self):
    expected = queues.mark_project_manual_update_time(self.redis,
                                                      b'Some_Project')
    actual = queues.next_update_time(self.redis, b'Some_Project')
    self.assertEqual(expected, actual)

  def test_get_project_queue_status_no_job(self):
    key = queues._update_job_status_key(b'Water')
    self.redis.hset(key, 'job_id', '1234-56')

    actual = queues.get_project_queue_status(self.redis, b'Water')
    self.assertIsNone(actual)

  @patch('wp1.queues.Job.fetch')
  def test_get_project_queue_status_job_finished(self, patched_fetch):
    job = MagicMock()
    patched_fetch.return_value = job
    expected_end = '2012-12-25'
    job.get_status.return_value = 'finished'
    job.ended_at = expected_end

    key = queues._update_job_status_key(b'Water')
    self.redis.hset(key, 'job_id', '1234-56')

    actual = queues.get_project_queue_status(self.redis, b'Water')
    self.assertEqual({'status': 'finished', 'ended_at': expected_end}, actual)

  @patch('wp1.queues.Queue')
  @patch('wp1.queues.logic_builder.materialize_builder')
  def test_enqueue_materialize(self, patched_materialize_builder,
                               patched_queue):
    materialize_q_mock = MagicMock()
    patched_queue.return_value = materialize_q_mock

    queues.enqueue_materialize(self.redis, SimpleBuilder, 1234,
                               'text/tab-separated-values')
    materialize_q_mock.enqueue.assert_called_once_with(
        patched_materialize_builder,
        SimpleBuilder,
        1234,
        'text/tab-separated-values',
        job_timeout=constants.JOB_TIMEOUT,
        failure_ttl=constants.JOB_FAILURE_TTL)

  @patch('wp1.queues.Queue')
  @patch('wp1.queues.Scheduler')
  def test_poll_for_zim_file_status(self, patched_scheduler, patched_queue):
    poll_q_mock = MagicMock()
    patched_queue.return_value = poll_q_mock
    scheduler_mock = MagicMock()
    patched_scheduler.return_value = scheduler_mock

    queues.poll_for_zim_file_status(self.redis, '1234')

    scheduler_mock.enqueue_in.assert_called_once()
