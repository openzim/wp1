import unittest
from unittest.mock import patch, Mock, MagicMock
import uuid

from wp1.base_db_test import BaseWpOneDbTest
from wp1.web.emails import respond_to_zim_task_completed
from wp1.web.emails_confirmation import send_zim_email_confirmation
from wp1.models.wp10.zim_file import ZimTask
from wp1.models.wp10.zim_schedule import ZimSchedule
from wp1.constants import TS_FORMAT_WP10
from wp1.timestamp import utcnow


class EmailConfirmationTest(BaseWpOneDbTest):

    def setUp(self):
        super().setUp()
        self.zim_task = ZimTask(
            z_id=12345,
            z_selection_id=b'test-selection-id',
            z_status=b'FILE_READY',
            z_task_id=b'test-task-id',
            z_zim_schedule_id=b'test-schedule-id'
        )

    @patch('wp1.web.emails.notify_user_for_scheduled_zim')
    @patch('wp1.logic.zim_schedules.decrement_remaining_generations')
    def test_respond_to_zim_task_completed_with_unconfirmed_email(self, 
                                                                   mock_decrement, 
                                                                   mock_notify):
        """Test that emails are NOT sent when confirmation token is present."""
        # Schedule with email but unconfirmed (has token)
        zim_schedule = ZimSchedule(
            s_id=b'test-schedule-id',
            s_builder_id=b'test-builder-id',
            s_email=b'test@example.com',
            s_email_confirmation_token=b'unconfirmed-token',
            s_rq_job_id=b'test-job-id',
            s_last_updated_at=utcnow().strftime(TS_FORMAT_WP10).encode('utf-8'),
            s_interval=3,
            s_remaining_generations=2
        )

        respond_to_zim_task_completed(self.wp10db, self.zim_task, zim_schedule)

        mock_decrement.assert_called_once_with(self.wp10db, b'test-schedule-id')
        mock_notify.assert_not_called()  # Should NOT send email

    @patch('wp1.web.emails.notify_user_for_scheduled_zim')
    @patch('wp1.logic.zim_schedules.decrement_remaining_generations')
    def test_respond_to_zim_task_completed_with_confirmed_email(self, 
                                                                 mock_decrement, 
                                                                 mock_notify):
        """Test that emails ARE sent when no confirmation token is present."""
        # Schedule with confirmed email (no token)
        zim_schedule = ZimSchedule(
            s_id=b'test-schedule-id',
            s_builder_id=b'test-builder-id',
            s_email=b'test@example.com',
            s_email_confirmation_token=None,  # Confirmed
            s_rq_job_id=b'test-job-id',
            s_last_updated_at=utcnow().strftime(TS_FORMAT_WP10).encode('utf-8'),
            s_interval=3,
            s_remaining_generations=2
        )

        respond_to_zim_task_completed(self.wp10db, self.zim_task, zim_schedule)

        mock_decrement.assert_called_once_with(self.wp10db, b'test-schedule-id')
        mock_notify.assert_called_once_with(self.wp10db, self.zim_task, zim_schedule)

    @patch('wp1.web.emails.notify_user_for_scheduled_zim')
    @patch('wp1.logic.zim_schedules.decrement_remaining_generations')
    def test_respond_to_zim_task_completed_with_no_email(self, 
                                                          mock_decrement, 
                                                          mock_notify):
        """Test that no emails are sent when no email is set."""
        # Schedule without email
        zim_schedule = ZimSchedule(
            s_id=b'test-schedule-id',
            s_builder_id=b'test-builder-id',
            s_email=None,
            s_email_confirmation_token=None,
            s_rq_job_id=b'test-job-id',
            s_last_updated_at=utcnow().strftime(TS_FORMAT_WP10).encode('utf-8'),
            s_interval=3,
            s_remaining_generations=2
        )

        respond_to_zim_task_completed(self.wp10db, self.zim_task, zim_schedule)

        mock_decrement.assert_called_once_with(self.wp10db, b'test-schedule-id')
        mock_notify.assert_not_called()  # Should NOT send email

    @patch('wp1.web.emails_confirmation.requests.post')
    @patch('wp1.web.emails_confirmation.CREDENTIALS')
    @patch('wp1.web.emails_confirmation.ENV', 'test')
    @patch('wp1.web.emails_confirmation.jinja_env')
    def test_send_zim_email_confirmation_success(self, mock_jinja_env, mock_credentials, mock_post):
        """Test successful confirmation email sending."""
        mock_credentials.get.return_value = {
            'MAILGUN': {
                'api_key': 'test-api-key',
                'url': 'https://api.mailgun.net/v3/test.com/messages'
            }
        }
        
        mock_template = Mock()
        mock_template.render.return_value = '<html>Confirmation email content</html>'
        mock_jinja_env.get_template.return_value = mock_template
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = send_zim_email_confirmation(
            recipient_username='testuser',
            recipient_email='test@example.com',
            zim_title='Test ZIM',
            confirm_url='https://example.com/confirm?token=abc123',
            unsubscribe_url='https://example.com/unsubscribe?token=abc123',
            repetition_period_months=3,
            number_of_repetitions=5
        )
        
        self.assertTrue(result)
        mock_jinja_env.get_template.assert_called_once_with('zim-email-confirmation.html.jinja2')
        mock_template.render.assert_called_once_with(
            user='testuser',
            title='Test ZIM',
            user_email='test@example.com',
            confirm_url='https://example.com/confirm?token=abc123',
            unsubscribe_url='https://example.com/unsubscribe?token=abc123',
            repetition_period_months=3,
            number_of_repetitions=5
        )
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], 'https://api.mailgun.net/v3/test.com/messages')
        self.assertEqual(call_args[1]['auth'], ('api', 'test-api-key'))
        
        email_data = call_args[1]['data']
        self.assertEqual(email_data['from'], 'Wikipedia WP 1.0 Project <notifications@mg.wp1.openzim.org>')
        self.assertEqual(email_data['to'], 'testuser <test@example.com>')
        self.assertEqual(email_data['subject'], 'Confirm Email Notifications for ZIM File - Test ZIM')
        self.assertIn('confirm your email address', email_data['text'])
        self.assertEqual(email_data['html'], '<html>Confirmation email content</html>')

    @patch('wp1.web.emails.CREDENTIALS')
    @patch('wp1.web.emails.ENV', 'test')
    def test_send_zim_email_confirmation_no_mailgun_config(self, mock_credentials):
        """Test confirmation email sending when Mailgun is not configured."""
        mock_credentials.get.return_value = {}
        
        result = send_zim_email_confirmation(
            recipient_username='testuser',
            recipient_email='test@example.com',
            zim_title='Test ZIM',
            confirm_url='https://example.com/confirm?token=abc123',
            unsubscribe_url='https://example.com/unsubscribe?token=abc123',
            repetition_period_months=3,
            number_of_repetitions=5
        )
        
        self.assertFalse(result)

    @patch('wp1.web.emails.requests.post')
    @patch('wp1.web.emails.CREDENTIALS')
    @patch('wp1.web.emails.ENV', 'test')
    @patch('wp1.web.emails.jinja_env')
    def test_send_zim_email_confirmation_api_error(self, mock_jinja_env, mock_credentials, mock_post):
        """Test confirmation email sending when API returns error."""
        mock_credentials.get.return_value = {
            'MAILGUN': {
                'api_key': 'test-api-key',
                'url': 'https://api.mailgun.net/v3/test.com/messages'
            }
        }
        
        mock_template = Mock()
        mock_template.render.return_value = '<html>Confirmation email content</html>'
        mock_jinja_env.get_template.return_value = mock_template
        
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = 'Bad Request'
        mock_post.return_value = mock_response
        
        result = send_zim_email_confirmation(
            recipient_username='testuser',
            recipient_email='test@example.com',
            zim_title='Test ZIM',
            confirm_url='https://example.com/confirm?token=abc123',
            unsubscribe_url='https://example.com/unsubscribe?token=abc123',
            repetition_period_months=3,
            number_of_repetitions=5
        )
        
        self.assertFalse(result)
