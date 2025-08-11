import attr
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
         (s_id, s_builder_id, s_rq_job_id, s_last_updated_at,
          s_interval, s_remaining_generations, s_email, s_title, s_description, s_long_description)
         VALUES
         (%(s_id)s, %(s_builder_id)s,  %(s_rq_job_id)s,
          %(s_last_updated_at)s, %(s_interval)s, %(s_remaining_generations)s,
          %(s_email)s, %(s_title)s, %(s_description)s, %(s_long_description)s)
      ''', attr.asdict(zim_schedule)
    )
  wp10db.commit()


def update_zim_schedule(wp10db, zim_schedule : ZimSchedule):
  """Updates a ZimSchedule record based on the model state. Returns True if updated."""
  with wp10db.cursor() as cursor:
    cursor.execute(
      '''UPDATE zim_schedules SET
         s_last_updated_at = %(s_last_updated_at)s,
         s_interval = %(s_interval)s,
         s_remaining_generations = %(s_remaining_generations)s,
         s_email = %(s_email)s,
         s_title = %(s_title)s,
         s_description = %(s_description)s,
         s_long_description = %(s_long_description)s
         WHERE s_id = %(s_id)s
      ''', attr.asdict(zim_schedule)
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


def get_zim_schedule_by_zim_file_id(wp10db, z_id):
  """Retrieves a ZimSchedule by its associated zim_file_id."""
  with wp10db.cursor() as cursor:
    cursor.execute(
      '''
      SELECT zs.* FROM zim_schedules zs
      JOIN zim_tasks zf ON zs.s_id = zf.z_zim_schedule_id
      WHERE zf.z_id = %s
      ''', (z_id,)
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


def decrement_remaining_generations(wp10db, schedule_id: bytes):
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
            'SELECT zs.* FROM zim_schedules zs JOIN zim_tasks zf ON zs.s_id = zf.z_zim_schedule_id WHERE zf.z_task_id = %s',
            (task_id,)
        )
        row = cursor.fetchone()
    if not row:
        return None
    return ZimSchedule(**row)

def get_username_by_zim_schedule_id(wp10db, schedule_id):
    """Retrieves the username associated with a ZimSchedule by its ID. Returns the username or None."""
    with wp10db.cursor() as cursor:
        cursor.execute(
            'SELECT u.u_username FROM zim_schedules zs JOIN users u ON zs.s_builder_id = u.u_id WHERE zs.s_id = %s',
            (schedule_id,)
        )
        row = cursor.fetchone()
    if not row:
        return None
    return row['u_username'].decode('utf-8') if row['u_username'] else None

def set_zim_schedule_id_to_zim_task_by_selection(wp10db, selection_id: bytes, zim_schedule_id: bytes):
    """Sets the z_zim_schedule_id field in zim_tasks to the given the selection_id."""
    with wp10db.cursor() as cursor:
        cursor.execute(
            'UPDATE zim_tasks SET z_zim_schedule_id = %s WHERE z_selection_id = %s',
            (zim_schedule_id, selection_id)
        )
        updated = bool(cursor.rowcount)
    wp10db.commit()
    return updated


def schedule_future_zimfile_generations(redis, wp10db, builder, zim_schedule_id: bytes, scheduled_repetitions):
  """
  Calculate timing and schedule future ZIM file creations using rq-scheduler, then save the schedule to the database.
  """

  required_keys = {'repetition_period_in_months', 'number_of_repetitions', 'email'}
  has_min_required_keys = required_keys <= scheduled_repetitions.keys()
  if not isinstance(scheduled_repetitions, dict) or not has_min_required_keys:
    raise ValueError(f'scheduled_repetitions must be a dict containing {required_keys}')

  period_months = scheduled_repetitions['repetition_period_in_months']
  interval_seconds = period_months * SECONDS_PER_MONTH
  first_future_run = utcnow() + relativedelta(seconds=interval_seconds)
  total_repetitions = scheduled_repetitions['number_of_repetitions']

  job = queues.schedule_recurring_zimfarm_task(
    redis=redis,
    args=[builder, zim_schedule_id],
    scheduled_time=first_future_run,
    interval_seconds=interval_seconds,
    repeat_count=total_repetitions - 1, # -1 because the first run is not counted as a repetition
  )

  zim_schedule: ZimSchedule = get_zim_schedule(wp10db, zim_schedule_id)
  zim_schedule.s_remaining_generations = total_repetitions
  zim_schedule.s_interval = period_months
  zim_schedule.s_rq_job_id = job.id.encode('utf-8')
  zim_schedule.s_email = scheduled_repetitions['email'].encode('utf-8')
  zim_schedule.set_last_updated_at_now()
  update_zim_schedule(wp10db, zim_schedule)

  return job.id