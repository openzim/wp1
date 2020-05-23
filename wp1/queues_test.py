import unittest
from unittest.mock import patch, MagicMock

from wp1.base_db_test import get_test_connect_creds
from wp1 import constants
from wp1.environment import Environment
from wp1 import queues


class QueuesTest(unittest.TestCase):

  @patch('wp1.queues.ENV', Environment.DEVELOPMENT)
  @patch('wp1.queues.CREDENTIALS', get_test_connect_creds())
  @patch('wp1.queues.logic_project.update_project_by_name')
  def test_enqueue_project_development(self, patched_project_fn):
    update_q = MagicMock()
    upload_q = MagicMock()

    queues.enqueue_project(b'Water', update_q, upload_q)

    update_q.enqueue.assert_called_once_with(patched_project_fn,
                                             b'Water',
                                             job_timeout=constants.JOB_TIMEOUT)
    upload_q.enqueue.assert_not_called()

  @patch('wp1.queues.ENV', Environment.PRODUCTION)
  @patch('wp1.queues.CREDENTIALS', get_test_connect_creds())
  @patch('wp1.queues.logic_project.update_project_by_name')
  @patch('wp1.queues.tables.upload_project_table')
  @patch('wp1.queues.logs.update_log_page_for_project')
  def test_enqueue_project_production(self, patched_log_fn, patched_tables_fn,
                                      patched_project_fn):
    update_q = MagicMock()
    upload_q = MagicMock()
    update_job = 'UPDATE JOB'
    update_q.enqueue.return_value = update_job
    project_name = b'Water'

    queues.enqueue_project(project_name, update_q, upload_q)

    update_q.enqueue.assert_called_once_with(patched_project_fn,
                                             project_name,
                                             job_timeout=constants.JOB_TIMEOUT)
    upload_q.enqueue.assert_any_call(patched_tables_fn,
                                     project_name,
                                     depends_on=update_job,
                                     job_timeout=constants.JOB_TIMEOUT)
    upload_q.enqueue.assert_any_call(patched_log_fn,
                                     project_name,
                                     depends_on=update_job,
                                     job_timeout=constants.JOB_TIMEOUT)

  @patch('wp1.queues.ENV', Environment.DEVELOPMENT)
  @patch('wp1.queues.CREDENTIALS', get_test_connect_creds())
  @patch('wp1.queues.Queue')
  @patch('wp1.queues.enqueue_project')
  def test_enequeue_single_project(self, patched_enqueue_project,
                                   patched_queue):
    update_q = MagicMock()
    upload_q = MagicMock
    patched_queue.side_effect = lambda name, connection=None: update_q if name == 'update' else upload_q

    queues.enqueue_single_project(b'Water')

    patched_enqueue_project.assert_called_once_with(b'Water', update_q,
                                                    upload_q)

  @patch('wp1.queues.ENV', Environment.DEVELOPMENT)
  @patch('wp1.queues.CREDENTIALS', get_test_connect_creds())
  @patch('wp1.queues.Queue')
  @patch('wp1.queues.enqueue_project')
  def test_enequeue_single_project(self, patched_enqueue_project,
                                   patched_queue):
    projects = (b'Water', b'Air', b'Fire', b'Earth')
    update_q = MagicMock()
    upload_q = MagicMock()
    patched_queue.side_effect = lambda name, connection=None: update_q if name == 'update' else upload_q

    queues.enqueue_multiple_projects(projects)

    for project_name in projects:
      patched_enqueue_project.assert_any_call(project_name, update_q, upload_q)

  @patch('wp1.queues.ENV', Environment.DEVELOPMENT)
  @patch('wp1.queues.CREDENTIALS', get_test_connect_creds())
  @patch('wp1.queues.logic_project.project_names_to_update')
  @patch('wp1.queues.wiki_connect')
  @patch('wp1.queues.Queue')
  @patch('wp1.queues.enqueue_project')
  def test_enqueue_all(self, patched_enqueue_project, patched_queue,
                       patched_db_connect, patched_names):
    projects = (b'Water', b'Air', b'Fire', b'Earth')
    patched_names.return_value = projects

    update_q = MagicMock()
    upload_q = MagicMock()
    update_q.count = 0
    upload_q.count = 0

    patched_queue.side_effect = lambda name, connection=None: update_q if name == 'update' else upload_q
    queues.enqueue_all_projects()

    for project_name in projects:
      patched_enqueue_project.assert_any_call(project_name, update_q, upload_q)
