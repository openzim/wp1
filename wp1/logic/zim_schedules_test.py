import datetime
import uuid
import time

from wp1.base_db_test import BaseWpOneDbTest
from wp1.logic.zim_schedules import (
    insert_zim_schedule,
    get_zim_schedule,
    list_zim_schedules_for_builder,
    update_zim_schedule,
    update_zim_schedule_zim_file_id,
    decrement_remaining_generations,
    get_scheduled_zimfarm_task_from_taskid
)
from wp1.models.wp10.zim_schedule import ZimSchedule
from wp1.constants import TS_FORMAT_WP10
from wp1.timestamp import utcnow

class LogicZimSchedulesTest(BaseWpOneDbTest):

  def new_schedule(self, builder_id=b'test-builder-id', interval=2, remaining=5):
    return ZimSchedule(
      s_id=str(uuid.uuid4()).encode('utf-8'),
      s_builder_id=builder_id,
      s_zim_file_id=None,
      s_rq_job_id='test-job-id'.encode('utf-8'),
      s_last_updated_at=utcnow().strftime(TS_FORMAT_WP10).encode('utf-8'),
      s_interval=interval,
      s_remaining_generations=remaining
    )

  def test_insert_and_get(self):
    schedule = self.new_schedule()
    insert_zim_schedule(self.wp10db, schedule)
    fetched = get_zim_schedule(self.wp10db, schedule.s_id)
    self.assertIsNotNone(fetched)
    self.assertEqual(schedule.s_id, fetched.s_id)
    self.assertEqual(schedule.s_builder_id, fetched.s_builder_id)
    self.assertEqual(schedule.s_interval,
                     fetched.s_interval)
    self.assertEqual(schedule.s_remaining_generations,
                     fetched.s_remaining_generations)

  def test_get_zim_schedule_returns_none_for_missing_id(self):
    # Try to fetch a schedule that does not exist
    missing_id = str(uuid.uuid4()).encode('utf-8')
    result = get_zim_schedule(self.wp10db, missing_id)
    self.assertIsNone(result) 

  def test_list_for_builder(self):
    b1 = b"test_builder_1"
    s1 = self.new_schedule(builder_id=b1, interval=1, remaining=1)
    s2 = self.new_schedule(builder_id=b1, interval=2, remaining=2)
    s3 = self.new_schedule(builder_id=b"test_builder_2", interval=3, remaining=3)
    insert_zim_schedule(self.wp10db, s1)
    insert_zim_schedule(self.wp10db, s2)
    insert_zim_schedule(self.wp10db, s3)

    lst = list_zim_schedules_for_builder(self.wp10db, b1)
    actual = sorted([s.s_id for s in lst])
    expected = sorted([s1.s_id, s2.s_id])
    self.assertEqual(expected, actual)

  def test_update_schedule(self):
    schedule = self.new_schedule(interval=1, remaining=1)
    insert_zim_schedule(self.wp10db, schedule)
    # Update fields
    schedule.s_zim_file_id = 999
    new_time = utcnow()
    schedule.s_last_updated_at = new_time.strftime(TS_FORMAT_WP10).encode('utf-8')
    schedule.s_interval = 5
    schedule.s_remaining_generations = 10
    ok = update_zim_schedule(self.wp10db, schedule)
    self.assertTrue(ok)
    fetched = get_zim_schedule(self.wp10db, schedule.s_id)
    self.assertEqual(999, fetched.s_zim_file_id)
    self.assertEqual(5, fetched.s_interval)
    self.assertEqual(10, fetched.s_remaining_generations)
    self.assertEqual(schedule.s_last_updated_at, fetched.s_last_updated_at)

  def test_update_schedule_zim_file_id(self):
    zim_schedule = self.new_schedule(interval=1, remaining=1)
    insert_zim_schedule(self.wp10db, zim_schedule)
    ok = update_zim_schedule_zim_file_id(self.wp10db, zim_schedule.s_id, 999)
    self.assertTrue(ok)
    fetched = get_zim_schedule(self.wp10db, zim_schedule.s_id)
    self.assertEqual(999, fetched.s_zim_file_id)

  def test_decrement_remaining_generations(self):
    schedule = self.new_schedule(remaining=2)
    insert_zim_schedule(self.wp10db, schedule)
    ok = decrement_remaining_generations(self.wp10db, schedule.s_id)
    self.assertTrue(ok)
    fetched = get_zim_schedule(self.wp10db, schedule.s_id)
    self.assertEqual(1, fetched.s_remaining_generations)
    # Decrement again
    ok = decrement_remaining_generations(self.wp10db, schedule.s_id)
    self.assertTrue(ok)
    fetched = get_zim_schedule(self.wp10db, schedule.s_id)
    self.assertEqual(0, fetched.s_remaining_generations)
  
  def test_decrement_remaining_generations_from_0(self):
    schedule = self.new_schedule(remaining=0)
    insert_zim_schedule(self.wp10db, schedule)
    # Should not go below zero
    ok = decrement_remaining_generations(self.wp10db, schedule.s_id)
    self.assertFalse(ok)
    fetched = get_zim_schedule(self.wp10db, schedule.s_id)
    self.assertEqual(0, fetched.s_remaining_generations)

  def test_decrement_remaining_generations_from_minus_1(self):
    schedule = self.new_schedule(remaining=-1)
    insert_zim_schedule(self.wp10db, schedule)
    # Should not change from -1
    ok = decrement_remaining_generations(self.wp10db, schedule.s_id)
    self.assertFalse(ok)
    fetched = get_zim_schedule(self.wp10db, schedule.s_id)
    self.assertEqual(-1, fetched.s_remaining_generations)

  def test_get_scheduled_zimfarm_task_from_taskid(self):
    # Insert a zim_file with a specific z_task_id
    zim_file_id = 12345
    z_task_id = str(uuid.uuid4()).encode('utf-8')
    z_selection_id = b"test_selection_id"
    with self.wp10db.cursor() as cursor:
      cursor.execute(
        'INSERT INTO zim_files (z_id, z_status, z_task_id, z_selection_id) VALUES (%s, %s, %s, %s)',
        (zim_file_id, 'NOT_REQUESTED', z_task_id, z_selection_id)
      )
    # Insert a schedule linked to the zim_file
    schedule = self.new_schedule()
    schedule.s_zim_file_id = zim_file_id
    insert_zim_schedule(self.wp10db, schedule)
    found = get_scheduled_zimfarm_task_from_taskid(self.wp10db, z_task_id)
    self.assertIsNotNone(found)
    self.assertEqual(zim_file_id, found.s_zim_file_id)
    self.assertEqual(schedule.s_id, found.s_id)

  def test_get_scheduled_zimfarm_task_from_taskid_is_none(self):
    # Insert a zim_file with a specific z_task_id
    zim_file_id = 12345
    z_task_id = str(uuid.uuid4()).encode('utf-8')
    z_selection_id = b"test_selection_id"
    with self.wp10db.cursor() as cursor:
      cursor.execute(
        'INSERT INTO zim_files (z_id, z_status, z_task_id, z_selection_id) VALUES (%s, %s, %s, %s)',
        (zim_file_id, 'NOT_REQUESTED', z_task_id, z_selection_id)
      ) 
    # No schedule yet
    self.assertIsNone(get_scheduled_zimfarm_task_from_taskid(self.wp10db, z_task_id))
    # Insert a schedule linked to the zim_file
    schedule = self.new_schedule()
    schedule.s_zim_file_id = zim_file_id
    insert_zim_schedule(self.wp10db, schedule)
    # Should return None for non-existent z_task_id
    self.assertIsNone(get_scheduled_zimfarm_task_from_taskid(self.wp10db, b"non_existent_task_id"))
