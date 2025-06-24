from datetime import datetime, timedelta, UTC
from dateutil.relativedelta import relativedelta
import logging
import uuid

from rq import Queue
import rq.exceptions
from rq.job import Job
from rq_scheduler import Scheduler

from wp1 import constants
from wp1 import custom_tables
from wp1.environment import Environment
import wp1.logic.builder as logic_builder
import wp1.logic.project as logic_project
import wp1.logic.zim_schedules as logic_zim_schedules
from wp1.wiki_db import connect as wiki_connect
from wp1 import logs
from wp1 import tables
from wp1.timestamp import utcnow
from wp1.credentials import ENV
from rq import get_current_job
from rq.registry import FinishedJobRegistry, FailedJobRegistry, CanceledJobRegistry

logger = logging.getLogger(__name__)


def _get_queues(redis, manual=False):
  prefix = 'manual-' if manual else ''

  update_q = Queue('%supdate' % prefix, connection=redis)
  upload_q = Queue('%supload' % prefix, connection=redis)

  return update_q, upload_q


def _get_materializer_queue(redis):
  return Queue('materializer', connection=redis)


def _get_zimfile_poll_queue(redis):
  return Queue('zimfile-polling', connection=redis)

def _get_zimfile_scheduling_queue(redis):
  return Queue('zimfile-scheduling', connection=redis)


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

def sum(a,b):
  return a + b

def poll_for_zim_file_status(redis, task_id):
  poll_q = _get_zimfile_poll_queue(redis)
  scheduler = Scheduler(queue=poll_q, connection=redis)
  scheduler.enqueue_in(timedelta(minutes=1),
                       logic_builder.on_zim_file_status_poll, task_id)

def schedule_future_zimfile_generations(redis, wp10db, builder, builder_id, title, description, long_description, scheduled_repetitions):
  """Schedule future ZIM file creations using rq-scheduler.
  
  Args:
      redis: Redis connection for job scheduling.
      wp10db: Database connection for WP10.
      builder: Builder instance to create ZIM files.
      builder_id: ID of the builder to schedule.
      title: Title of the ZIM file.
      description: Description of the ZIM file.
      long_description: Long description of the ZIM file.
      scheduled_repetitions: Dict containing repetition details.
  """
  if not isinstance(scheduled_repetitions, dict):
    raise ValueError('scheduled_repetitions must be a dict')
  if 'repetition_period_in_months' not in scheduled_repetitions:
    raise ValueError('scheduled_repetitions must contain repetition_period_in_months')
  if 'number_of_repetitions' not in scheduled_repetitions:
    raise ValueError('scheduled_repetitions must contain number_of_repetitions')

  queue = _get_zimfile_scheduling_queue(redis)
  scheduler = Scheduler(connection=queue.connection, queue=queue)

  period_months = scheduled_repetitions['repetition_period_in_months']
  num_repetitions = scheduled_repetitions['number_of_repetitions']
  
  first_run = datetime.now(UTC) + relativedelta(months=period_months)
  now = datetime.now(UTC)
  interval_seconds = int((first_run - now).total_seconds())

  job = scheduler.schedule(
    scheduled_time=first_run,
    func=logic_builder.request_zimfile_from_zimfarm,
    args=[builder, builder_id, title, description, long_description],
    kwargs={'rebuild_selection': True},
    interval=interval_seconds,
    repeat=num_repetitions,
    queue_name='zimfile-scheduling'
  )

  # Insert the new schedule into the zim_schedules table using the model
  from wp1.models.wp10.zim_schedule import ZimSchedule
  zim_schedule = ZimSchedule(
      s_id=str(uuid.uuid4()),
      s_builder_id=builder_id,
      s_zim_file_id=None,
      s_rq_job_id=job.id,
      s_last_updated_at=datetime.now(UTC).strftime(constants.TS_FORMAT_WP10).encode('utf-8'),
      s_interval_between_zim_generations=period_months,
      s_remaining_generations=num_repetitions
  )
  logic_zim_schedules.insert_zim_schedule(wp10db, zim_schedule)

  return job.id