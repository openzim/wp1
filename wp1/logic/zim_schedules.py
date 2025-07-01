import attr

from wp1.constants import TS_FORMAT_WP10
from wp1.timestamp import utcnow
from wp1.models.wp10.zim_schedule import ZimSchedule


def insert_zim_schedule(wp10db, zim_schedule : ZimSchedule):
  """Inserts a ZimSchedule into the zim_schedules table"""
  with wp10db.cursor() as cursor:
    cursor.execute(
      '''INSERT INTO zim_schedules
         (s_id, s_builder_id, s_zim_file_id, s_rq_job_id, s_last_updated_at,
          s_interval_between_zim_generations, s_remaining_generations)
         VALUES
         (%(s_id)s, %(s_builder_id)s, %(s_zim_file_id)s, %(s_rq_job_id)s,
          %(s_last_updated_at)s, %(s_interval_between_zim_generations)s, %(s_remaining_generations)s)
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
         s_interval_between_zim_generations = %(s_interval_between_zim_generations)s,
         s_remaining_generations = %(s_remaining_generations)s
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
        if not row or row['s_remaining_generations'] is None:
            return False
        current = row['s_remaining_generations']
        if current <= 0:
            new_value = 0
        else:
            new_value = current - 1
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

