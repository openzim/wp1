import logging

from redis import Redis
from rq import Queue

from wp1 import constants
from wp1.environment import Environment
import wp1.logic.project as logic_project
from wp1.wiki_db import connect as wiki_connect
from wp1 import logs
from wp1 import tables

logger = logging.getLogger(__name__)

try:
  from wp1.credentials import ENV, CREDENTIALS
except ImportError:
  logger.exception('The file credentials.py must be populated manually in '
                   'order to connect to Redis')
  CREDENTIALS = None
  ENV = None

logger = logging.getLogger(__name__)


def enqueue_all_projects():
  creds = CREDENTIALS[ENV]['REDIS']

  update_q = Queue('update', connection=Redis(**creds))
  upload_q = Queue('upload', connection=Redis(**creds))

  if (update_q.count > 0 or upload_q.count > 0):
    logger.error('Queues are not empty. Refusing to add more work.')
    return

  wikidb = wiki_connect()
  for project_name in logic_project.project_names_to_update(wikidb):
    enqueue_project(project_name, update_q, upload_q)


def enqueue_multiple_projects(project_names):
  creds = CREDENTIALS[ENV]['REDIS']

  update_q = Queue('update', connection=Redis(**creds))
  upload_q = Queue('upload', connection=Redis(**creds))

  for project_name in project_names:
    enqueue_project(project_name, update_q, upload_q)


def enqueue_single_project(project_name):
  creds = CREDENTIALS[ENV]['REDIS']

  update_q = Queue('update', connection=Redis(**creds))
  upload_q = Queue('upload', connection=Redis(**creds))

  enqueue_project(project_name, update_q, upload_q)


def enqueue_project(project_name, update_q, upload_q):
  logger.info('Enqueuing update %s', project_name)
  update_job = update_q.enqueue(logic_project.update_project_by_name,
                                project_name,
                                job_timeout=constants.JOB_TIMEOUT)
  if ENV == Environment.PRODUCTION:
    logger.info('Enqueuing upload (dependent) %s', project_name)
    upload_q.enqueue(tables.upload_project_table,
                     project_name,
                     depends_on=update_job,
                     job_timeout=constants.JOB_TIMEOUT)
    logger.info('Enqueuing log upload (dependent) %s', project_name)
    upload_q.enqueue(logs.update_log_page_for_project,
                     project_name,
                     depends_on=update_job,
                     job_timeout=constants.JOB_TIMEOUT)
  else:
    logger.warning('Skipping enqueuing the upload job because environment is '
                   'not PRODUCTION')
