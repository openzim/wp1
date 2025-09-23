import unittest
import uuid
from unittest.mock import patch

from wp1.base_db_test import BaseWpOneDbTest
from wp1.logic.zim_schedules import (
    find_active_recurring_schedule_for_builder,
    delete_zim_schedule,
    insert_zim_schedule,
    get_zim_schedule
)
from wp1.models.wp10.zim_schedule import ZimSchedule
from wp1.timestamp import utcnow
from wp1.constants import TS_FORMAT_WP10


class LogicZimSchedulesActiveTest(BaseWpOneDbTest):

    def new_schedule(self, builder_id=b'builder-id', interval=2, remaining=5, rq_job_id=b'job-id'):
        return ZimSchedule(
            s_id=str(uuid.uuid4()).encode('utf-8'),
            s_builder_id=builder_id,
            s_rq_job_id=rq_job_id,
            s_last_updated_at=utcnow().strftime(TS_FORMAT_WP10).encode('utf-8'),
            s_interval=interval,
            s_remaining_generations=remaining,
            s_long_description=b'Test long description',
            s_description=b'Test description',
            s_title=b'Test title'
        )

    def test_find_active_recurring_schedule_for_builder_with_active_schedule(self):
        """Test finding an active recurring schedule (remaining_generations > 0)."""
        builder_id = b'active-builder-id'
        
        # Insert an active schedule
        active_schedule = self.new_schedule(builder_id=builder_id, remaining=3)
        insert_zim_schedule(self.wp10db, active_schedule)
        
        # Insert a completed schedule (remaining = 0)
        completed_schedule = self.new_schedule(builder_id=builder_id, remaining=0)
        insert_zim_schedule(self.wp10db, completed_schedule)
        
        result = find_active_recurring_schedule_for_builder(self.wp10db, builder_id)
        
        self.assertIsNotNone(result)
        self.assertEqual(active_schedule.s_id, result.s_id)
        self.assertEqual(3, result.s_remaining_generations)

    def test_find_active_recurring_schedule_for_builder_no_active_schedule(self):
        """Test when no active recurring schedule exists."""
        builder_id = b'inactive-builder-id'
        
        # Insert only completed schedules
        completed_schedule1 = self.new_schedule(builder_id=builder_id, remaining=0)
        insert_zim_schedule(self.wp10db, completed_schedule1)
        
        completed_schedule2 = self.new_schedule(builder_id=builder_id, remaining=None)
        insert_zim_schedule(self.wp10db, completed_schedule2)
        
        result = find_active_recurring_schedule_for_builder(self.wp10db, builder_id)
        
        self.assertIsNone(result)

    def test_find_active_recurring_schedule_for_builder_no_schedules(self):
        """Test when no schedules exist for the builder."""
        builder_id = b'nonexistent-builder-id'
        
        result = find_active_recurring_schedule_for_builder(self.wp10db, builder_id)
        
        self.assertIsNone(result)

    @patch('wp1.queues.cancel_scheduled_job')
    def test_delete_zim_schedule_success(self, mock_cancel_job):
        """Test successful deletion of a ZIM schedule."""
        mock_cancel_job.return_value = True
        
        schedule = self.new_schedule()
        insert_zim_schedule(self.wp10db, schedule)
        
        # Verify the schedule exists
        retrieved_schedule = get_zim_schedule(self.wp10db, schedule.s_id)
        self.assertIsNotNone(retrieved_schedule)
        
        # Delete the schedule
        deleted = delete_zim_schedule(self.redis, self.wp10db, schedule.s_id)
        
        self.assertTrue(deleted)
        mock_cancel_job.assert_called_once_with(self.redis, schedule.s_rq_job_id)
        
        # Verify the schedule is deleted
        retrieved_schedule = get_zim_schedule(self.wp10db, schedule.s_id)
        self.assertIsNone(retrieved_schedule)

    @patch('wp1.queues.cancel_scheduled_job')
    def test_delete_zim_schedule_nonexistent(self, mock_cancel_job):
        """Test deletion of a non-existent schedule."""
        nonexistent_id = str(uuid.uuid4()).encode('utf-8')
        
        deleted = delete_zim_schedule(self.redis, self.wp10db, nonexistent_id)
        
        self.assertFalse(deleted)
        mock_cancel_job.assert_not_called()

    @patch('wp1.queues.cancel_scheduled_job')
    def test_delete_zim_schedule_no_rq_job(self, mock_cancel_job):
        """Test deletion of a schedule with no RQ job ID."""
        schedule = self.new_schedule(rq_job_id=None)
        insert_zim_schedule(self.wp10db, schedule)
        
        deleted = delete_zim_schedule(self.redis, self.wp10db, schedule.s_id)
        
        self.assertTrue(deleted)
        mock_cancel_job.assert_not_called()
        
        # Verify the schedule is deleted
        retrieved_schedule = get_zim_schedule(self.wp10db, schedule.s_id)
        self.assertIsNone(retrieved_schedule)


if __name__ == '__main__':
    unittest.main()
