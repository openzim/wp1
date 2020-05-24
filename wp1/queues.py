from datetime import timedelta
import logging

from rq import Queue

from wp1 import constants
from wp1.environment import Environment
import wp1.logic.project as logic_project
from wp1.wiki_db import connect as wiki_connect
from wp1 import logs
from wp1 import tables
from wp1.timestamp import utcnow

logger = logging.getLogger(__name__)

try:
  from wp1.credentials import ENV
except ImportError:
  logger.exception('The file credentials.py must be populated manually in '
                   'order to connect to Redis')
  ENV = None

logger = logging.getLogger(__name__)


def _get_queues(redis, manual=False):
  prefix = 'manual-' if manual else ''

  update_q = Queue('%supdate' % prefix, connection=redis)
  upload_q = Queue('%supload' % prefix, connection=redis)

  return update_q, upload_q


def enqueue_all_projects(redis):
  update_q, upload_q = _get_queues(redis)

  if (update_q.count > 0 or upload_q.count > 0):
    logger.error('Queues are not empty. Refusing to add more work.')
    return

  wikidb = wiki_connect()
  for project_name in logic_project.project_names_to_update(wikidb):
    enqueue_project(project_name, update_q, upload_q)


def enqueue_multiple_projects(redis, project_names):
  update_q, upload_q = _get_queues(redis)

  for project_name in project_names:
    enqueue_project(project_name, update_q, upload_q)


def enqueue_single_project(redis, project_name, manual=False):
  update_q, upload_q = _get_queues(redis, manual=manual)

  enqueue_project(project_name, update_q, upload_q)


def _manual_key(project_name):
  return b'manual_update_time:%s' % project_name


def next_update_time(redis, project_name):
  key = _manual_key(project_name)
  ts = redis.get(key)
  if ts is not None:
    ts = ts.decode('utf-8')
  return ts


def mark_project_manual_update_time(redis, project_name):
  key = _manual_key(project_name)
  ts = (utcnow() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M UTC')
  redis.setex(key, timedelta(hours=1), value=ts)
  return ts


def enqueue_project(project_name, update_q, upload_q):
  logger.warning(update_q.name)
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
