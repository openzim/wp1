import unittest
from unittest.mock import patch, MagicMock, ANY
import uuid

from wp1.base_db_test import BaseWpOneDbTest
from wp1.logic import zim_schedules
from wp1.models.wp10.zim_schedule import ZimSchedule
from wp1.constants import TS_FORMAT_WP10
from wp1.timestamp import utcnow


class ZimSchedulesEmailConfirmationTest(BaseWpOneDbTest):

    def setUp(self):
        super().setUp()
        self.schedule_id = str(uuid.uuid4()).encode('utf-8')
        self.builder_id = str(uuid.uuid4()).encode('utf-8')
        self.token = zim_schedules.generate_email_confirmation_token()
        
        self.zim_schedule = ZimSchedule(
            s_id=self.schedule_id,
            s_builder_id=self.builder_id,
            s_rq_job_id=b'test-job-id',
            s_last_updated_at=utcnow().strftime(TS_FORMAT_WP10).encode('utf-8'),
            s_interval=3,
            s_remaining_generations=5,
            s_email=b'test@example.com',
            s_title=b'Test ZIM Schedule',
            s_description=b'Test description',
            s_long_description=b'Test long description',
            s_email_confirmation_token=self.token
        )

    def test_generate_email_confirmation_token(self):
        """Test that a token is generated and is valid."""
        token = zim_schedules.generate_email_confirmation_token()
        self.assertIsInstance(token, bytes)
        self.assertTrue(len(token) > 20)  # Should be a reasonable length

    def test_insert_zim_schedule_with_token(self):
        """Test inserting a schedule with email confirmation token."""
        zim_schedules.insert_zim_schedule(self.wp10db, self.zim_schedule)
        
        fetched = zim_schedules.get_zim_schedule(self.wp10db, self.schedule_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(self.token, fetched.s_email_confirmation_token)
        self.assertEqual(b'test@example.com', fetched.s_email)

    def test_get_zim_schedule_by_token(self):
        """Test retrieving a schedule by its confirmation token."""
        zim_schedules.insert_zim_schedule(self.wp10db, self.zim_schedule)
        
        fetched = zim_schedules.get_zim_schedule_by_token(self.wp10db, self.token)
        self.assertIsNotNone(fetched)
        self.assertEqual(self.schedule_id, fetched.s_id)
        self.assertEqual(self.token, fetched.s_email_confirmation_token)

    def test_get_zim_schedule_by_token_not_found(self):
        """Test retrieving a schedule by non-existent token."""
        fake_token = b'non-existent-token'
        fetched = zim_schedules.get_zim_schedule_by_token(self.wp10db, fake_token)
        self.assertIsNone(fetched)

    def test_confirm_email_subscription(self):
        """Test confirming email subscription by removing token."""
        zim_schedules.insert_zim_schedule(self.wp10db, self.zim_schedule)
        
        success = zim_schedules.confirm_email_subscription(self.wp10db, self.token)
        self.assertTrue(success)
        
        # Verify token was removed
        fetched = zim_schedules.get_zim_schedule(self.wp10db, self.schedule_id)
        self.assertIsNone(fetched.s_email_confirmation_token)
        self.assertEqual(b'test@example.com', fetched.s_email)  # Email should remain

    def test_confirm_email_subscription_invalid_token(self):
        """Test confirming with invalid token."""
        fake_token = b'invalid-token'
        success = zim_schedules.confirm_email_subscription(self.wp10db, fake_token)
        self.assertFalse(success)

    def test_unsubscribe_email(self):
        """Test unsubscribing from email notifications."""
        zim_schedules.insert_zim_schedule(self.wp10db, self.zim_schedule)
        
        success = zim_schedules.unsubscribe_email(self.wp10db, self.token)
        self.assertTrue(success)
        
        # Verify both email and token were removed
        fetched = zim_schedules.get_zim_schedule(self.wp10db, self.schedule_id)
        self.assertIsNone(fetched.s_email_confirmation_token)
        self.assertIsNone(fetched.s_email)

    def test_unsubscribe_email_invalid_token(self):
        """Test unsubscribing with invalid token."""
        fake_token = b'invalid-token'
        success = zim_schedules.unsubscribe_email(self.wp10db, fake_token)
        self.assertFalse(success)

    @patch('wp1.logic.zim_schedules.send_zim_email_confirmation')
    @patch('wp1.logic.zim_schedules.get_username_by_zim_schedule_id')
    @patch('wp1.queues.schedule_recurring_zimfarm_task')
    def test_schedule_future_zimfile_generations_with_email_sends_confirmation(self, 
                                                                               mock_schedule_task,
                                                                               mock_get_username,
                                                                               mock_send_confirmation):
        """Test that scheduling with email sends confirmation email."""
        job_mock = MagicMock()
        job_mock.id = 'test-job-id'
        mock_schedule_task.return_value = job_mock
        mock_get_username.return_value = 'testuser'
        mock_send_confirmation.return_value = True
        
        schedule_without_email = ZimSchedule(
            s_id=self.schedule_id,
            s_builder_id=self.builder_id,
            s_rq_job_id=None,
            s_last_updated_at=utcnow().strftime(TS_FORMAT_WP10).encode('utf-8'),
            s_title=b'Test ZIM Schedule'
        )
        zim_schedules.insert_zim_schedule(self.wp10db, schedule_without_email)
        
        scheduled_repetitions = {
            'repetition_period_in_months': 2,
            'number_of_repetitions': 3,
            'email': 'test@example.com'
        }
        
        builder = MagicMock()
        zim_schedules.schedule_future_zimfile_generations(
            redis=MagicMock(),
            wp10db=self.wp10db,
            builder=builder,
            zim_schedule_id=self.schedule_id,
            scheduled_repetitions=scheduled_repetitions
        )
        
        # Verify confirmation email was sent
        mock_send_confirmation.assert_called_once_with(
            recipient_username='testuser',
            recipient_email='test@example.com',
            zim_title='Test ZIM Schedule',
            confirm_url=ANY,
            unsubscribe_url=ANY,
            repetition_period_months=2,
            number_of_repetitions=3
        )
        
        # Verify schedule has token
        fetched = zim_schedules.get_zim_schedule(self.wp10db, self.schedule_id)
        self.assertIsNotNone(fetched.s_email_confirmation_token)
        self.assertEqual(b'test@example.com', fetched.s_email)

    @patch('wp1.queues.schedule_recurring_zimfarm_task')
    def test_schedule_future_zimfile_generations_without_email_no_token(self, mock_schedule_task):
        """Test that scheduling without email doesn't generate token."""
        job_mock = MagicMock()
        job_mock.id = 'test-job-id'
        mock_schedule_task.return_value = job_mock
        
        schedule_without_email = ZimSchedule(
            s_id=self.schedule_id,
            s_builder_id=self.builder_id,
            s_rq_job_id=None,
            s_last_updated_at=utcnow().strftime(TS_FORMAT_WP10).encode('utf-8'),
            s_title=b'Test ZIM Schedule'
        )
        zim_schedules.insert_zim_schedule(self.wp10db, schedule_without_email)
        
        scheduled_repetitions = {
            'repetition_period_in_months': 2,
            'number_of_repetitions': 3
        }
        
        builder = MagicMock()
        zim_schedules.schedule_future_zimfile_generations(
            redis=MagicMock(),
            wp10db=self.wp10db,
            builder=builder,
            zim_schedule_id=self.schedule_id,
            scheduled_repetitions=scheduled_repetitions
        )
        
        # Verify no token was generated
        fetched = zim_schedules.get_zim_schedule(self.wp10db, self.schedule_id)
        self.assertIsNone(fetched.s_email_confirmation_token)
        self.assertIsNone(fetched.s_email)
