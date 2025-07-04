import unittest
from unittest.mock import ANY, patch, MagicMock

import fakeredis

from wp1.base_db_test import BaseWpOneDbTest
from wp1 import constants
from wp1.environment import Environment
from wp1 import queues  
from wp1.models.wp10.builder import Builder
from wp1.selection.models.simple import Builder as SimpleBuilder


class QueuesTest(BaseWpOneDbTest):

  def setUp(self):
    super().setUp()

  def tearDown(self):
    super().tearDown()

  @patch('wp1.queues.ENV', Environment.DEVELOPMENT)
  @patch('wp1.queues.logic_project.update_project_by_name')
  def test_enqueue_project_development(self, mock_project_fn):
    update_q = MagicMock()
    upload_q = MagicMock()

    queues.enqueue_project(b'Water', update_q, upload_q)

    update_q.enqueue.assert_called_once_with(
        mock_project_fn,
        b'Water',
        job_timeout=constants.JOB_TIMEOUT,
        failure_ttl=constants.JOB_FAILURE_TTL,
        track_progress=False)
    upload_q.enqueue.assert_not_called()

  @patch('wp1.queues.ENV', Environment.PRODUCTION)
  @patch('wp1.queues.logic_project.update_project_by_name')
  @patch('wp1.queues.tables.upload_project_table')
  @patch('wp1.queues.logs.update_log_page_for_project')
  def test_enqueue_project_production(self, mock_log_fn, mock_tables_fn,
                                      mock_project_fn):
    update_q = MagicMock()
    upload_q = MagicMock()
    update_job = MagicMock()
    update_job.id = '1234-567'
    update_q.enqueue.return_value = update_job
    project_name = b'Water'

    queues.enqueue_project(project_name, update_q, upload_q)

    update_q.enqueue.assert_called_once_with(
        mock_project_fn,
        project_name,
        job_timeout=constants.JOB_TIMEOUT,
        failure_ttl=constants.JOB_FAILURE_TTL,
        track_progress=False)
    upload_q.enqueue.assert_any_call(mock_tables_fn,
                                     project_name,
                                     depends_on=update_job,
                                     job_timeout=constants.JOB_TIMEOUT,
                                     failure_ttl=constants.JOB_FAILURE_TTL)
    upload_q.enqueue.assert_any_call(mock_log_fn,
                                     project_name,
                                     depends_on=update_job,
                                     job_timeout=constants.JOB_TIMEOUT,
                                     failure_ttl=constants.JOB_FAILURE_TTL)

  @patch('wp1.queues.ENV', Environment.DEVELOPMENT)
  @patch('wp1.queues.Queue')
  @patch('wp1.queues.enqueue_project')
  def test_enqueue_single_project(self, mock_enqueue_project, mock_queue):
    update_q = MagicMock()
    upload_q = MagicMock

    mock_queue.side_effect = lambda name, connection=None: update_q if name == 'update' else upload_q

    queues.enqueue_single_project(self.redis, b'Water')

    mock_enqueue_project.assert_called_once_with(b'Water',
                                                    update_q,
                                                    upload_q,
                                                    redis=self.redis,
                                                    track_progress=False)

  @patch('wp1.queues.ENV', Environment.DEVELOPMENT)
  @patch('wp1.queues.custom_tables.upload_custom_table_by_name')
  @patch('wp1.queues.Queue')
  @patch('wp1.queues.enqueue_project')
  def test_enqueue_multipe_projects(self, mock_enqueue_project,
                                    mock_queue, mock_upload):
    projects = (b'Water', b'Air', b'Fire', b'Earth')
    update_q = MagicMock()
    upload_q = MagicMock()
    mock_queue.side_effect = lambda name, connection=None: update_q if name == 'update' else upload_q

    queues.enqueue_custom_table(self.redis, b'Water')

    upload_q.enqueue.assert_any_call(mock_upload,
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
  def test_enqueue_all(self, mock_enqueue_custom, mock_enqueue_project,
                       mock_queue, mock_db_connect, mock_custom_names,
                       mock_names):
    projects = (b'Water', b'Air', b'Fire', b'Earth')
    mock_names.return_value = projects
    custom_names = (b'North', b'South', b'East', b'West')
    mock_custom_names.return_value = custom_names

    update_q = MagicMock()
    upload_q = MagicMock()
    update_q.count = 0
    upload_q.count = 0

    mock_queue.side_effect = lambda name, connection=None: update_q if name == 'update' else upload_q

    queues.enqueue_all_projects(self.redis, self.wp10db)

    for project_name in projects:
      mock_enqueue_project.assert_any_call(project_name, update_q, upload_q)

    for name in custom_names:
      mock_enqueue_custom.assert_any_call(self.redis, name)

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
  def test_get_project_queue_status_job_finished(self, mock_fetch):
    job = MagicMock()
    mock_fetch.return_value = job
    expected_end = '2012-12-25'
    job.get_status.return_value = 'finished'
    job.ended_at = expected_end

    key = queues._update_job_status_key(b'Water')
    self.redis.hset(key, 'job_id', '1234-56')

    actual = queues.get_project_queue_status(self.redis, b'Water')
    self.assertEqual({'status': 'finished', 'ended_at': expected_end}, actual)

  @patch('wp1.queues.Queue')
  @patch('wp1.queues.logic_builder.materialize_builder')
  def test_enqueue_materialize(self, mock_materialize_builder,
                               mock_queue):
    materialize_q_mock = MagicMock()
    mock_queue.return_value = materialize_q_mock
    builder = MagicMock()
    queues.enqueue_materialize(self.redis, SimpleBuilder, builder, 'text/tab-separated-values')
    materialize_q_mock.enqueue.assert_called_once_with(
        mock_materialize_builder,
        SimpleBuilder,
        builder,
        'text/tab-separated-values',
        job_timeout=constants.JOB_TIMEOUT,
        failure_ttl=constants.JOB_FAILURE_TTL)

  @patch('wp1.queues.Queue')
  @patch('wp1.queues.Scheduler')
  def test_poll_for_zim_file_status(self, mock_scheduler, mock_queue):
    poll_q_mock = MagicMock()
    mock_queue.return_value = poll_q_mock
    scheduler_mock = MagicMock()
    mock_scheduler.return_value = scheduler_mock

    queues.poll_for_zim_file_status(self.redis, '1234')

    scheduler_mock.enqueue_in.assert_called_once()

  @patch('wp1.queues.Scheduler')
  @patch('wp1.queues.uuid.uuid4')
  def test_schedule_future_zimfile_generations(self, mock_uuid4, mock_scheduler):
    builder = Builder(
        b_id=b'builder-id',
        b_name=b'Test Builder',
        b_user_id=b'1234',
        b_project=b'en.wikipedia.fake',
        b_model=b'wp1.selection.models.simple',
        b_params=b'{}',
    )
    title = 'Title'
    description = 'Description'
    long_description = 'Long Description'
    scheduled_repetitions = {
        'repetition_period_in_months': 2,
        'number_of_repetitions': 3,
        'email': 'user@example.com'
    }
    job_mock = MagicMock()
    job_mock.id = 'job-id'
    mock_scheduler.return_value.schedule.return_value = job_mock
    mock_uuid4.return_value = 'uuid-1'

    result = queues.schedule_future_zimfile_generations(
        self.redis, self.wp10db,
        builder, title, description, long_description,
        scheduled_repetitions
    )

    self.assertEqual('job-id', result)
    # Verify scheduler.schedule was called with correct parameters
    mock_scheduler.return_value.schedule.assert_called_once()
    _, call_kwargs = mock_scheduler.return_value.schedule.call_args
    self.assertEqual(queues.logic_builder.request_scheduled_zim_file_for_builder, call_kwargs['func'])

    expected_args = [builder, title, description, long_description, ANY]
    self.assertEqual(expected_args, call_kwargs['args'])
    expected_interval = scheduled_repetitions['repetition_period_in_months'] * 30 * 24 * 3600
    self.assertEqual(expected_interval, call_kwargs['interval'])
    self.assertEqual(scheduled_repetitions['number_of_repetitions'], call_kwargs['repeat'])
    self.assertEqual('zimfile-scheduling', call_kwargs['queue_name'])

    with self.wp10db.cursor() as cursor:
      cursor.execute('SELECT * FROM zim_schedules WHERE s_id = %s', (b'uuid-1',))
      zim_schedule = cursor.fetchone()
      self.assertIsNotNone(zim_schedule)
      self.assertEqual(b'uuid-1', zim_schedule['s_id'])
      self.assertEqual(b'builder-id', zim_schedule['s_builder_id'])
      self.assertEqual(b'job-id', zim_schedule['s_rq_job_id'])
      self.assertEqual(scheduled_repetitions['repetition_period_in_months'], zim_schedule['s_interval'])
      self.assertEqual(scheduled_repetitions['number_of_repetitions'], zim_schedule['s_remaining_generations'])
  
  def test_schedule_future_zimfile_generations_missing_fields(self):
    
    builder = Builder(
        b_id=b'builder-id',
        b_name=b'Test Builder',
        b_user_id=b'1234',
        b_project=b'en.wikipedia.fake',
        b_model=b'wp1.selection.models.simple',
        b_params=b'{}',
    )
    title = 'Title'
    description = 'Description'
    long_description = 'Long Description'
    scheduled_repetitions = {
        'repetition_period_in_months': 2,
        'number_of_repetitions': 3,
    }

    with self.assertRaises(ValueError):
      queues.schedule_future_zimfile_generations(
          self.redis, self.wp10db,
          builder, title, description, long_description,
          scheduled_repetitions
      )
      