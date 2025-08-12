import uuid
from unittest.mock import patch, MagicMock, ANY

from wp1.base_db_test import BaseWpOneDbTest
from wp1.logic.zim_schedules import *
from wp1.models.wp10.zim_schedule import ZimSchedule
from wp1.models.wp10.builder import Builder
from wp1.constants import TS_FORMAT_WP10, SECONDS_PER_MONTH
from wp1.timestamp import utcnow

class LogicZimSchedulesTest(BaseWpOneDbTest):

  def new_schedule(self, builder_id=b'builder-id', interval=2, remaining=5):
    return ZimSchedule(
      s_id=str(uuid.uuid4()).encode('utf-8'),
      s_builder_id=builder_id,
      s_rq_job_id='job-id'.encode('utf-8'),
      s_last_updated_at=utcnow().strftime(TS_FORMAT_WP10).encode('utf-8'),
      s_interval=interval,
      s_remaining_generations=remaining,
      s_long_description=b'Test long description',
      s_description=b'Test description',
      s_title=b'Test title'
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

  def test_get_zim_schedule_by_zim_file_id_returns_none_for_missing_id(self):
    # Try to fetch a schedule that does not exist
    missing_id = str(uuid.uuid4()).encode('utf-8')
    result = get_zim_schedule_by_zim_file_id(self.wp10db, missing_id)
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
    new_time = utcnow()
    schedule.s_last_updated_at = new_time.strftime(TS_FORMAT_WP10).encode('utf-8')
    schedule.s_interval = 5
    schedule.s_remaining_generations = 10
    schedule.s_title = b'New Title'
    ok = update_zim_schedule(self.wp10db, schedule)
    self.assertTrue(ok)
    fetched = get_zim_schedule(self.wp10db, schedule.s_id)
    self.assertEqual(5, fetched.s_interval)
    self.assertEqual(10, fetched.s_remaining_generations)
    self.assertEqual(schedule.s_last_updated_at, fetched.s_last_updated_at)
    self.assertEqual(b'New Title', fetched.s_title)

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
    # Insert a schedule linked to the zim_file
    schedule = self.new_schedule()
    insert_zim_schedule(self.wp10db, schedule)
    with self.wp10db.cursor() as cursor:
      cursor.execute(
        'INSERT INTO zim_tasks (z_id, z_status, z_task_id, z_selection_id, z_zim_schedule_id) VALUES (%s, %s, %s, %s, %s)',
        (zim_file_id, 'NOT_REQUESTED', z_task_id, z_selection_id, schedule.s_id)
      )
    found = get_scheduled_zimfarm_task_from_taskid(self.wp10db, z_task_id)
    self.assertIsNotNone(found)
    self.assertEqual(schedule.s_id, found.s_id)

  def test_get_scheduled_zimfarm_task_from_taskid_is_none(self):
    # Insert a zim_file with a specific z_task_id
    zim_file_id = 12345
    z_task_id = str(uuid.uuid4()).encode('utf-8')
    z_selection_id = b"test_selection_id"
    # No schedule yet
    self.assertIsNone(get_scheduled_zimfarm_task_from_taskid(self.wp10db, z_task_id))
    # Insert a schedule linked to the zim_file
    schedule = self.new_schedule()
    insert_zim_schedule(self.wp10db, schedule)
    with self.wp10db.cursor() as cursor:
      cursor.execute(
        'INSERT INTO zim_tasks (z_id, z_status, z_task_id, z_selection_id, z_zim_schedule_id) VALUES (%s, %s, %s, %s, %s)',
        (zim_file_id, 'NOT_REQUESTED', z_task_id, z_selection_id, b'schedule_123')
      )
    # Should return None for non-existent z_task_id
    self.assertIsNone(get_scheduled_zimfarm_task_from_taskid(self.wp10db, b"non_existent_task_id"))

  @patch('wp1.queues.schedule_recurring_zimfarm_task')
  def test_schedule_future_zimfile_generations(self, mock_schedule_recurring_zimfarm_task):
    builder = Builder(
        b_id=b'builder-id',
        b_name=b'Test Builder',
        b_user_id=b'1234',
        b_project=b'en.wikipedia.fake',
        b_model=b'wp1.selection.models.simple',
        b_params=b'{}',
    )
    scheduled_repetitions = {
        'repetition_period_in_months': 2,
        'number_of_repetitions': 3,
        'email': 'user@example.com'
    }
    job_mock = MagicMock()
    job_mock.id = 'job-id'
    mock_schedule_recurring_zimfarm_task.return_value = job_mock

    zim_schedule = self.new_schedule()
    insert_zim_schedule(self.wp10db, zim_schedule)

    result = schedule_future_zimfile_generations(
        self.redis, self.wp10db,
        builder, zim_schedule.s_id,
        scheduled_repetitions
    )
    two_months_in_seconds = SECONDS_PER_MONTH * 2
    self.assertEqual('job-id', result)
    # Verify scheduler.schedule was called with correct parameters
    mock_schedule_recurring_zimfarm_task.assert_called_once_with(
      redis=self.redis,
      args=[builder, zim_schedule.s_id],
      scheduled_time=ANY,
      interval_seconds=two_months_in_seconds,
      repeat_count=scheduled_repetitions['number_of_repetitions'] - 1
    )

    with self.wp10db.cursor() as cursor:
      cursor.execute('SELECT * FROM zim_schedules WHERE s_id = %s', (zim_schedule.s_id,))
      actual_zim_schedule = cursor.fetchone()
      self.assertIsNotNone(actual_zim_schedule)
      self.assertEqual(zim_schedule.s_id, actual_zim_schedule['s_id'])
      self.assertEqual(b'builder-id', actual_zim_schedule['s_builder_id'])
      self.assertEqual(b'job-id', actual_zim_schedule['s_rq_job_id'])
      self.assertEqual(scheduled_repetitions['email'].encode('utf-8'), actual_zim_schedule['s_email'])
      self.assertEqual(scheduled_repetitions['repetition_period_in_months'], actual_zim_schedule['s_interval'])
      self.assertEqual(scheduled_repetitions['number_of_repetitions'], actual_zim_schedule['s_remaining_generations'])

  def test_schedule_future_zimfile_generations_missing_fields(self):
    builder = Builder(
        b_id=b'builder-id',
        b_name=b'Test Builder',
        b_user_id=b'1234',
        b_project=b'en.wikipedia.fake',
        b_model=b'wp1.selection.models.simple',
        b_params=b'{}',
    )
    scheduled_repetitions = {
        'repetition_period_in_months': 2,
        'number_of_repetitions': 3,
        # Missing 'email' field
    }
    zim_schedule = self.new_schedule()
    insert_zim_schedule(self.wp10db, zim_schedule)

    with self.assertRaises(ValueError):
      schedule_future_zimfile_generations(
          self.redis, self.wp10db,
          builder, zim_schedule.s_id,
          scheduled_repetitions
      )

  def test_get_username_by_zim_schedule_id_found(self):
    # Insert user and schedule
    user_id = b'user-123'
    username = 'testuser'
    with self.wp10db.cursor() as cursor:
      cursor.execute(
        'INSERT INTO users (u_id, u_username) VALUES (%s, %s)',
        (user_id, username.encode('utf-8'))
      )
    schedule = self.new_schedule(builder_id=user_id)
    insert_zim_schedule(self.wp10db, schedule)
    result = get_username_by_zim_schedule_id(self.wp10db, schedule.s_id)
    self.assertEqual(username, result)

  def test_get_username_by_zim_schedule_id_username_is_none(self):
    # Insert user with null username and schedule
    user_id = b'user-456'
    with self.wp10db.cursor() as cursor:
      cursor.execute(
        'INSERT INTO users (u_id, u_username) VALUES (%s, %s)',
        (user_id, None)
      )
    schedule = self.new_schedule(builder_id=user_id)
    insert_zim_schedule(self.wp10db, schedule)
    result = get_username_by_zim_schedule_id(self.wp10db, schedule.s_id)
    self.assertIsNone(result)

  def test_get_username_by_zim_schedule_id_not_found(self):
    # No such schedule or user
    missing_id = b'not-a-real-schedule'
    result = get_username_by_zim_schedule_id(self.wp10db, missing_id)
    self.assertIsNone(result)

  def test_set_zim_schedule_id_to_zim_task_by_selection_success(self):
        zim_file_id = 55555
        z_selection_id = b"sel_id_abc"
        z_task_id = b"task_id_abc"
        schedule = self.new_schedule()
        insert_zim_schedule(self.wp10db, schedule)
        with self.wp10db.cursor() as cursor:
            cursor.execute(
                'INSERT INTO zim_tasks (z_id, z_status, z_task_id, z_selection_id) VALUES (%s, %s, %s, %s)',
                (zim_file_id, 'NOT_REQUESTED', z_task_id, z_selection_id)
            )
        updated = set_zim_schedule_id_to_zim_task_by_selection(self.wp10db, z_selection_id, schedule.s_id)
        self.assertTrue(updated)
        with self.wp10db.cursor() as cursor:
            cursor.execute('SELECT z_zim_schedule_id FROM zim_tasks WHERE z_selection_id = %s', (z_selection_id,))
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row['z_zim_schedule_id'], schedule.s_id)

  def test_set_zim_schedule_id_to_zim_task_by_selection_no_match(self):
      z_selection_id = b"nonexistent_sel"
      schedule = self.new_schedule()
      insert_zim_schedule(self.wp10db, schedule)
      updated = set_zim_schedule_id_to_zim_task_by_selection(self.wp10db, z_selection_id, schedule.s_id)
      self.assertFalse(updated)
      with self.wp10db.cursor() as cursor:
          cursor.execute('SELECT * FROM zim_tasks WHERE z_selection_id = %s', (z_selection_id,))
          row = cursor.fetchone()
          self.assertIsNone(row)