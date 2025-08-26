import unittest
from unittest.mock import patch, MagicMock
import uuid

from wp1.base_db_test import BaseWpOneDbTest
from wp1.web.app import create_app
from wp1.logic import zim_schedules
from wp1.models.wp10.zim_schedule import ZimSchedule
from wp1.constants import TS_FORMAT_WP10
from wp1.timestamp import utcnow


class ZimEmailsEndpointsTest(BaseWpOneDbTest):

    def setUp(self):
        super().setUp()
        self.app = create_app()
        self.token = zim_schedules.generate_email_confirmation_token()
        self.schedule_id = str(uuid.uuid4()).encode('utf-8')
        
        self.zim_schedule = ZimSchedule(
            s_id=self.schedule_id,
            s_builder_id=str(uuid.uuid4()).encode('utf-8'),
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

    def test_confirm_email_success(self):
        """Test successful email confirmation."""
        # Insert schedule with token
        zim_schedules.insert_zim_schedule(self.wp10db, self.zim_schedule)
        
        with self.app.test_client() as client:
            response = client.get(f'/v1/zim/confirm-email?token={self.token.decode("utf-8")}')
            
            self.assertEqual(200, response.status_code)
            self.assertIn(b'Email Confirmed Successfully', response.data)
            self.assertIn(b'Test ZIM Schedule', response.data)
        
        # Verify token was removed
        fetched = zim_schedules.get_zim_schedule(self.wp10db, self.schedule_id)
        self.assertIsNone(fetched.s_email_confirmation_token)
        self.assertEqual(b'test@example.com', fetched.s_email)

    def test_confirm_email_missing_token(self):
        """Test email confirmation with missing token."""
        with self.app.test_client() as client:
            response = client.get('/v1/zim/confirm-email')
            
            self.assertEqual(400, response.status_code)
            self.assertIn(b'Invalid Confirmation Link', response.data)

    def test_confirm_email_invalid_token(self):
        """Test email confirmation with invalid token."""
        with self.app.test_client() as client:
            response = client.get('/v1/zim/confirm-email?token=invalid-token')
            
            self.assertEqual(404, response.status_code)
            self.assertIn(b'Invalid or Expired Confirmation Link', response.data)

    def test_confirm_email_already_confirmed(self):
        """Test email confirmation with already used token."""
        # Insert schedule and confirm once
        zim_schedules.insert_zim_schedule(self.wp10db, self.zim_schedule)
        zim_schedules.confirm_email_subscription(self.wp10db, self.token)
        
        with self.app.test_client() as client:
            response = client.get(f'/v1/zim/confirm-email?token={self.token.decode("utf-8")}')
            
            self.assertEqual(404, response.status_code)
            self.assertIn(b'Invalid or Expired Confirmation Link', response.data)

    def test_unsubscribe_email_success(self):
        """Test successful email unsubscribe."""
        # Insert schedule with token
        zim_schedules.insert_zim_schedule(self.wp10db, self.zim_schedule)
        
        with self.app.test_client() as client:
            response = client.get(f'/v1/zim/unsubscribe-email?token={self.token.decode("utf-8")}')
            
            self.assertEqual(200, response.status_code)
            self.assertIn(b'Successfully Unsubscribed', response.data)
            self.assertIn(b'Test ZIM Schedule', response.data)
        
        # Verify both email and token were removed
        fetched = zim_schedules.get_zim_schedule(self.wp10db, self.schedule_id)
        self.assertIsNone(fetched.s_email_confirmation_token)
        self.assertIsNone(fetched.s_email)

    def test_unsubscribe_email_missing_token(self):
        """Test email unsubscribe with missing token."""
        with self.app.test_client() as client:
            response = client.get('/v1/zim/unsubscribe-email')
            
            self.assertEqual(400, response.status_code)
            self.assertIn(b'Invalid Unsubscribe Link', response.data)

    def test_unsubscribe_email_invalid_token(self):
        """Test email unsubscribe with invalid token."""
        with self.app.test_client() as client:
            response = client.get('/v1/zim/unsubscribe-email?token=invalid-token')
            
            self.assertEqual(404, response.status_code)
            self.assertIn(b'Invalid or Expired Unsubscribe Link', response.data)

    def test_unsubscribe_email_already_unsubscribed(self):
        """Test email unsubscribe with already used token."""
        # Insert schedule and unsubscribe once
        zim_schedules.insert_zim_schedule(self.wp10db, self.zim_schedule)
        zim_schedules.unsubscribe_email(self.wp10db, self.token)
        
        with self.app.test_client() as client:
            response = client.get(f'/v1/zim/unsubscribe-email?token={self.token.decode("utf-8")}')
            
            self.assertEqual(404, response.status_code)
            self.assertIn(b'Invalid or Expired Unsubscribe Link', response.data)

    def test_unsubscribe_notification_success(self):
        """Test notification unsubscribe success using schedule ID."""
        # Insert confirmed schedule (no token)
        confirmed_schedule = ZimSchedule(
            s_id=self.schedule_id,
            s_builder_id=str(uuid.uuid4()).encode('utf-8'),
            s_rq_job_id=b'test-job-id',
            s_last_updated_at=utcnow().strftime(TS_FORMAT_WP10).encode('utf-8'),
            s_interval=3,
            s_remaining_generations=5,
            s_email=b'test@example.com',
            s_title=b'Test ZIM Schedule',
            s_description=b'Test description',
            s_long_description=b'Test long description',
            s_email_confirmation_token=None  # Confirmed email
        )
        zim_schedules.insert_zim_schedule(self.wp10db, confirmed_schedule)
        
        with self.app.test_client() as client:
            response = client.get(f'/v1/zim/unsubscribe-notification?schedule_id={self.schedule_id.decode("utf-8")}')
            
            self.assertEqual(200, response.status_code)
            self.assertIn(b'Successfully Unsubscribed', response.data)
            self.assertIn(b'Test ZIM Schedule', response.data)
            
            # Verify email was removed from database
            updated_schedule = zim_schedules.get_zim_schedule(self.wp10db, self.schedule_id)
            self.assertIsNone(updated_schedule.s_email)

    def test_unsubscribe_notification_missing_schedule_id(self):
        """Test notification unsubscribe without schedule_id parameter."""
        with self.app.test_client() as client:
            response = client.get('/v1/zim/unsubscribe-notification')
            
            self.assertEqual(400, response.status_code)
            self.assertIn(b'Invalid Unsubscribe Link', response.data)

    def test_unsubscribe_notification_invalid_schedule_id(self):
        """Test notification unsubscribe with invalid schedule ID."""
        with self.app.test_client() as client:
            response = client.get('/v1/zim/unsubscribe-notification?schedule_id=invalid-schedule-id')
            
            self.assertEqual(404, response.status_code)
            self.assertIn(b'Invalid or Already Unsubscribed', response.data)

    def test_unsubscribe_notification_no_email(self):
        """Test notification unsubscribe for schedule without email."""
        # Insert schedule without email
        schedule_no_email = ZimSchedule(
            s_id=self.schedule_id,
            s_builder_id=str(uuid.uuid4()).encode('utf-8'),
            s_rq_job_id=b'test-job-id',
            s_last_updated_at=utcnow().strftime(TS_FORMAT_WP10).encode('utf-8'),
            s_interval=3,
            s_remaining_generations=5,
            s_email=None,  # No email
            s_title=b'Test ZIM Schedule',
            s_description=b'Test description',
            s_long_description=b'Test long description',
            s_email_confirmation_token=None
        )
        zim_schedules.insert_zim_schedule(self.wp10db, schedule_no_email)
        
        with self.app.test_client() as client:
            response = client.get(f'/v1/zim/unsubscribe-notification?schedule_id={self.schedule_id.decode("utf-8")}')
            
            self.assertEqual(404, response.status_code)
            self.assertIn(b'Invalid or Already Unsubscribed', response.data)
