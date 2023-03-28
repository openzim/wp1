from datetime import timedelta
import logging

from rq import Queue
import rq.exceptions
from rq.job import Job
from rq_scheduler import Scheduler

from wp1 import constants
from wp1 import custom_tables
from wp1.environment import Environment
import wp1.logic.builder as logic_builder
import wp1.logic.project as logic_project
from wp1.wiki_db import connect as wiki_connect
from wp1 import logs
from wp1 import redis_db
from wp1 import tables
from wp1.timestamp import utcnow

logger = logging.getLogger(__name__)

try:
  from wp1.credentials import ENV
except ImportError:
  logger.exception('The file credentials.py must be populated manually in '
                   'order to connect to Redis')
  ENV = None


def _get_queues(redis, manual=False):
  prefix = 'manual-' if manual else ''

  update_q = Queue('%supdate' % prefix, connection=redis)
  upload_q = Queue('%supload' % prefix, connection=redis)

  return update_q, upload_q


def _get_materializer_queue(redis):
  return Queue('materializer', connection=redis)


def _get_zimfile_poll_queue(redis):
  return Queue('zimfile-polling', connection=redis)


def enqueue_all_projects(redis, wp10db):
  update_q, upload_q = _get_queues(redis)

  if (update_q.count > 0 or upload_q.count > 0):
    logger.error('Queues are not empty. Refusing to add more work.')
    return

  # Enqueue all regular WikiProjects as queried from the Wiki DB
  wikidb = wiki_connect()
  for project_name in logic_project.project_names_to_update(wikidb):
    enqueue_project(project_name, update_q, upload_q)

  # Enqueue all active custom tables, as found in the WP10 DB
  for custom_name in custom_tables.all_custom_table_names(wp10db):
    enqueue_custom_table(redis, custom_name)


def enqueue_multiple_projects(redis, project_names):
  update_q, upload_q = _get_queues(redis)

  for project_name in project_names:
    enqueue_project(project_name, update_q, upload_q)


def enqueue_single_project(redis, project_name, manual=False):
  update_q, upload_q = _get_queues(redis, manual=manual)

  if manual:
    logic_project.clear_project_progress(redis, project_name)

  enqueue_project(project_name,
                  update_q,
                  upload_q,
                  redis=redis,
                  track_progress=manual)


def enqueue_custom_table(redis, custom_name):
  _, upload_q = _get_queues(redis)

  upload_q.enqueue(custom_tables.upload_custom_table_by_name,
                   custom_name,
                   job_timeout=constants.JOB_TIMEOUT,
                   failure_ttl=constants.JOB_FAILURE_TTL)


def _manual_key(project_name):
  return b'manual_update_time:%s' % project_name


def _update_job_status_key(project_name):
  return b'update_job_status:%s' % project_name


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


def get_project_queue_status(redis, project_name):
  key = _update_job_status_key(project_name)
  job_id = redis.hmget(key, 'job_id')

  if not job_id or not job_id[0]:
    logger.info('No redis data for key: %s', key)
    return None

  job_id = job_id[0].decode('utf-8')
  try:
    job = Job.fetch(job_id, connection=redis)
  except rq.exceptions.NoSuchJobError:
    logger.info('No such job with id: %s', job_id)
    return None

  status = job.get_status()
  if status == 'finished':
    return {'status': status, 'ended_at': job.ended_at}
  return {'status': status}


def set_project_update_job_id(redis, project_name, job_id):
  if redis is None:
    logger.error(
        'Attempt to track progress without specifying a Redis instance')
    return

  key = _update_job_status_key(project_name)
  redis.hset(key, mapping={'job_id': job_id})


def enqueue_project(project_name,
                    update_q,
                    upload_q,
                    redis=None,
                    track_progress=False):
  logger.info('Enqueuing update %s', project_name)
  update_job = update_q.enqueue(logic_project.update_project_by_name,
                                project_name,
                                track_progress=track_progress,
                                job_timeout=constants.JOB_TIMEOUT,
                                failure_ttl=constants.JOB_FAILURE_TTL)
  set_project_update_job_id(redis, project_name, update_job.id)
  if ENV == Environment.PRODUCTION:
    logger.info('Enqueuing upload (dependent) %s', project_name)
    upload_q.enqueue(tables.upload_project_table,
                     project_name,
                     depends_on=update_job,
                     job_timeout=constants.JOB_TIMEOUT,
                     failure_ttl=constants.JOB_FAILURE_TTL)
    logger.info('Enqueuing log upload (dependent) %s', project_name)
    upload_q.enqueue(logs.update_log_page_for_project,
                     project_name,
                     depends_on=update_job,
                     job_timeout=constants.JOB_TIMEOUT,
                     failure_ttl=constants.JOB_FAILURE_TTL)
  else:
    logger.warning('Skipping enqueuing the upload job because environment is '
                   'not PRODUCTION')


def enqueue_materialize(redis, builder_cls, builder_id, content_type):
  materialize_q = _get_materializer_queue(redis)
  materialize_q.enqueue(logic_builder.materialize_builder,
                        builder_cls,
                        builder_id,
                        content_type,
                        job_timeout=constants.JOB_TIMEOUT,
                        failure_ttl=constants.JOB_FAILURE_TTL)


def poll_for_zim_file_status(redis, task_id):
  poll_q = _get_zimfile_poll_queue(redis)
  scheduler = Scheduler(queue=poll_q, connection=redis)
  scheduler.enqueue_in(timedelta(minutes=2),
                       logic_builder.on_zim_file_status_poll, task_id)
