import attr
import uuid
from dateutil.relativedelta import relativedelta
import wp1.queues as queues

from wp1.constants import TS_FORMAT_WP10, SECONDS_PER_MONTH
from wp1.timestamp import utcnow
from wp1.models.wp10.zim_schedule import ZimSchedule


def insert_zim_schedule(wp10db, zim_schedule : ZimSchedule):
  """Inserts a ZimSchedule into the zim_schedules table"""
  with wp10db.cursor() as cursor:
    cursor.execute(
      '''INSERT INTO zim_schedules
         (s_id, s_builder_id, s_zim_file_id, s_rq_job_id, s_last_updated_at,
          s_interval, s_remaining_generations)
         VALUES
         (%(s_id)s, %(s_builder_id)s, %(s_zim_file_id)s, %(s_rq_job_id)s,
          %(s_last_updated_at)s, %(s_interval)s, %(s_remaining_generations)s)
      ''', attr.asdict(zim_schedule)
    )
  wp10db.commit()


def update_zim_schedule(wp10db, zim_schedule : ZimSchedule):
  """Updates a ZimSchedule record based on the model state. Returns True if updated."""
  with wp10db.cursor() as cursor:
    cursor.execute(
      '''UPDATE zim_schedules SET
         s_zim_file_id = %(s_zim_file_id)s,
         s_last_updated_at = %(s_last_updated_at)s,
         s_interval = %(s_interval)s,
         s_remaining_generations = %(s_remaining_generations)s
         WHERE s_id = %(s_id)s
      ''', attr.asdict(zim_schedule)
    )
    updated = bool(cursor.rowcount)
  wp10db.commit()
  return updated


def update_zim_schedule_zim_file_id(wp10db, schedule_id, zim_file_id):
  """Updates the s_zim_file_id of a ZimSchedule by its s_id. Returns True if updated."""
  updated_at = utcnow().strftime(TS_FORMAT_WP10).encode('utf-8')
  with wp10db.cursor() as cursor:
    cursor.execute(
      '''UPDATE zim_schedules SET
         s_zim_file_id = %s,
         s_last_updated_at = %s
         WHERE s_id = %s
      ''', (zim_file_id, updated_at, schedule_id)
    )
    updated = bool(cursor.rowcount)
  wp10db.commit()
  return updated


def get_zim_schedule(wp10db, schedule_id):
  """Retrieves a ZimSchedule by its s_id. Returns a ZimSchedule or None."""
  with wp10db.cursor() as cursor:
    cursor.execute(
      'SELECT * FROM zim_schedules WHERE s_id = %s', (schedule_id,)
    )
    row = cursor.fetchone()
  if not row:
    return None
  return ZimSchedule(**row)


def list_zim_schedules_for_builder(wp10db, builder_id):
  """Lists all ZimSchedule entries for a given builder_id."""
  with wp10db.cursor() as cursor:
    cursor.execute(
      'SELECT * FROM zim_schedules WHERE s_builder_id = %s', (builder_id,)
    )
    rows = cursor.fetchall()
  return [
    ZimSchedule(**row) for row in rows
  ]

def decrement_remaining_generations(wp10db, schedule_id):
    """Decrements s_remaining_generations by 1 for the given schedule, not going below 0. Also updates s_last_updated_at. Returns True if updated."""
    updated_at = utcnow().strftime(TS_FORMAT_WP10).encode('utf-8')
    with wp10db.cursor() as cursor:
        cursor.execute(
            'SELECT s_remaining_generations FROM zim_schedules WHERE s_id = %s', (schedule_id,)
        )
        row = cursor.fetchone()
        if not row or not row['s_remaining_generations'] or row['s_remaining_generations'] <= 0:
            return False
        new_value = row['s_remaining_generations'] - 1
        cursor.execute(
            'UPDATE zim_schedules SET s_remaining_generations = %s, s_last_updated_at = %s WHERE s_id = %s',
            (new_value, updated_at, schedule_id)
        )
        updated = bool(cursor.rowcount)
    wp10db.commit()
    return updated


def get_scheduled_zimfarm_task_from_taskid(wp10db, task_id):
    """Checks if a task_id is scheduled in zim_schedules. Returns the ZimSchedule if found, else None."""
    with wp10db.cursor() as cursor:
        cursor.execute(
            'SELECT zs.* FROM zim_schedules zs JOIN zim_files zf ON zs.s_zim_file_id = zf.z_id WHERE zf.z_task_id = %s',
            (task_id,)
        )
        row = cursor.fetchone()
    if not row:
        return None
    return ZimSchedule(**row)


def create_zim_schedule_with_job(wp10db, builder, scheduled_repetitions, job_id, schedule_id=None):
    """Create and save a ZimSchedule with the given RQ job information."""
    required_keys = {'repetition_period_in_months', 'number_of_repetitions', 'email'}
    has_min_required_keys = required_keys <= scheduled_repetitions.keys()
    if not isinstance(scheduled_repetitions, dict) or not has_min_required_keys:
        raise ValueError(f'scheduled_repetitions must be a dict containing {required_keys}')

    period_months = scheduled_repetitions['repetition_period_in_months']
    num_scheduled_repetitions = scheduled_repetitions['number_of_repetitions']
    
    if schedule_id is None:
        schedule_id = str(uuid.uuid4())
    
    zim_schedule = ZimSchedule(
        s_id=schedule_id.encode('utf-8'),
        s_builder_id=builder.b_id,
        s_zim_file_id=None,
        s_rq_job_id=job_id.encode('utf-8'),
        s_interval=period_months,
        s_remaining_generations=num_scheduled_repetitions,
        # s_email=scheduled_repetitions['email'].encode('utf-8')
    )
    zim_schedule.set_last_updated_at_now()
    insert_zim_schedule(wp10db, zim_schedule)
    
    return schedule_id


def schedule_future_zimfile_generations(redis, wp10db, builder, title, description, long_description, scheduled_repetitions):
  """
  Calculate timing and schedule future ZIM file creations using rq-scheduler, then save the schedule to the database.
  """
  period_months = scheduled_repetitions['repetition_period_in_months']
  interval_seconds = period_months * SECONDS_PER_MONTH
  first_future_run = utcnow() + relativedelta(seconds=interval_seconds)
  zim_schedule_id = str(uuid.uuid4())

  job = queues.schedule_recurring_zimfarm_task(
    redis=redis,
    args=[builder, title, description, long_description, zim_schedule_id],
    scheduled_time=first_future_run,
    interval_seconds=interval_seconds,
    repeat_count=scheduled_repetitions['number_of_repetitions'] - 1,
  )

  create_zim_schedule_with_job(wp10db, builder, scheduled_repetitions, job.id, zim_schedule_id)
  return job.id

