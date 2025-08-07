from unittest.mock import Mock, patch
import uuid

from wp1.base_db_test import BaseWpOneDbTest
from wp1.web.emails import send_zim_ready_email, notify_user_for_scheduled_zim
from wp1.models.wp10.zim_schedule import ZimSchedule
from wp1.models.wp10.zim_file import ZimTask
from wp1.constants import TS_FORMAT_WP10
from wp1.timestamp import utcnow


class EmailsTest(BaseWpOneDbTest):

    def setUp(self):
        super().setUp()
        self.mock_zim_task = ZimTask(
            z_id=b'test-zim-id',
            z_selection_id=b'test-selection-id',
            z_status=b'COMPLETED',
            z_task_id=b'test-task-id',
            z_title=b'Test ZIM Task',
            z_description=b'Test description',
            z_long_description=b'Test long description'
        )
        
        self.mock_zim_schedule = ZimSchedule(
            s_id=str(uuid.uuid4()).encode('utf-8'),
            s_builder_id=b'test-builder-id',
            s_zim_file_id=b'test-zim-file-id',
            s_email=b'test@example.com',
            s_rq_job_id=b'test-job-id',
            s_last_updated_at=utcnow().strftime(TS_FORMAT_WP10).encode('utf-8'),
            s_interval=3,
            s_remaining_generations=2
        )

    @patch('wp1.web.emails.requests.post')
    @patch('wp1.web.emails.CREDENTIALS')
    @patch('wp1.web.emails.ENV', 'test')
    @patch('wp1.web.emails.jinja_env')
    def test_send_zim_ready_email(self, mock_jinja_env, mock_credentials, mock_post):
        """Test successful email sending."""
        mock_credentials.get.return_value = {
            'MAILGUN': {
                'api_key': 'test-api-key',
                'url': 'https://api.mailgun.net/v3/test.com/messages'
            }
        }
        
        mock_template = Mock()
        mock_template.render.return_value = '<html>Test email content</html>'
        mock_jinja_env.get_template.return_value = mock_template
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = send_zim_ready_email(
            recipient_username='testuser',
            recipient_email='test@example.com',
            zim_title='Test ZIM',
            download_url='https://download.example.com/test.zim',
            manage_schedule_url='https://manage.example.com',
            unsubscribe_url='https://unsubscribe.example.com',
            next_generation_months=3
        )
        
        self.assertTrue(result)
        mock_jinja_env.get_template.assert_called_once_with('generated-scheduled-zim-email.html.jinja2')
        mock_template.render.assert_called_once_with(
            user='testuser',
            title='Test ZIM',
            download_url='https://download.example.com/test.zim',
            manage_schedule_url='https://manage.example.com',
            unsubscribe_url='https://unsubscribe.example.com',
            block_email='https://unsubscribe.example.com',
            next_generation_months=3
        )
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], 'https://api.mailgun.net/v3/test.com/messages')
        self.assertEqual(call_args[1]['auth'], ('api', 'test-api-key'))
        
        email_data = call_args[1]['data']
        self.assertEqual(email_data['from'], 'Wikipedia WP 1.0 Project <notifications@mg.wp1.openzim.org>')
        self.assertEqual(email_data['to'], 'testuser <test@example.com>')
        self.assertEqual(email_data['subject'], 'Your ZIM File is Ready for Download - Test ZIM')
        self.assertIn('Test ZIM', email_data['text'])
        self.assertEqual(email_data['html'], '<html>Test email content</html>')

    @patch('wp1.web.emails.requests.post')
    @patch('wp1.web.emails.CREDENTIALS')
    @patch('wp1.web.emails.ENV', 'test')
    @patch('wp1.web.emails.jinja_env')
    def test_send_zim_ready_email_with_defaults(self, mock_jinja_env, mock_credentials, mock_post):
        """Test email sending with default URLs."""
        mock_credentials.get.return_value = {
            'MAILGUN': {
                'api_key': 'test-api-key',
                'url': 'https://api.mailgun.net/v3/test.com/messages'
            }
        }
        
        mock_template = Mock()
        mock_template.render.return_value = '<html>Test email content</html>'
        mock_jinja_env.get_template.return_value = mock_template
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = send_zim_ready_email(
            recipient_username='testuser',
            recipient_email='test@example.com',
            zim_title='Test ZIM',
            download_url='https://download.example.com/test.zim'
        )
        
        self.assertTrue(result)
        mock_template.render.assert_called_once_with(
            user='testuser',
            title='Test ZIM',
            download_url='https://download.example.com/test.zim',
            manage_schedule_url='#',
            unsubscribe_url='#',
            block_email='#',
            next_generation_months=None
        )

    @patch('wp1.web.emails.CREDENTIALS')
    @patch('wp1.web.emails.ENV', 'test')
    def test_send_zim_ready_email_no_mailgun_config(self, mock_credentials):
        """Test email sending when Mailgun is not configured."""
        mock_credentials.get.return_value = {}
        
        result = send_zim_ready_email(
            recipient_username='testuser',
            recipient_email='test@example.com',
            zim_title='Test ZIM',
            download_url='https://download.example.com/test.zim'
        )
        
        self.assertFalse(result)

    @patch('wp1.web.emails.CREDENTIALS')
    @patch('wp1.web.emails.ENV', 'test')
    def test_send_zim_ready_email_no_api_key(self, mock_credentials):
        """Test email sending when API key is missing."""
        mock_credentials.get.return_value = {
            'MAILGUN': {
                'url': 'https://api.mailgun.net/v3/test.com/messages'
            }
        }
        
        result = send_zim_ready_email(
            recipient_username='testuser',
            recipient_email='test@example.com',
            zim_title='Test ZIM',
            download_url='https://download.example.com/test.zim'
        )
        
        self.assertFalse(result)

    @patch('wp1.web.emails.requests.post')
    @patch('wp1.web.emails.CREDENTIALS')
    @patch('wp1.web.emails.ENV', 'test')
    @patch('wp1.web.emails.jinja_env')
    def test_send_zim_ready_email_api_error(self, mock_jinja_env, mock_credentials, mock_post):
        """Test email sending when API returns an error."""
        mock_credentials.get.return_value = {
            'MAILGUN': {
                'api_key': 'test-api-key',
                'url': 'https://api.mailgun.net/v3/test.com/messages'
            }
        }
        
        mock_template = Mock()
        mock_template.render.return_value = '<html>Test email content</html>'
        mock_jinja_env.get_template.return_value = mock_template
        
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = 'Bad Request'
        mock_post.return_value = mock_response
        
        result = send_zim_ready_email(
            recipient_username='testuser',
            recipient_email='test@example.com',
            zim_title='Test ZIM',
            download_url='https://download.example.com/test.zim'
        )
        
        self.assertFalse(result)

    @patch('wp1.web.emails.requests.post')
    @patch('wp1.web.emails.CREDENTIALS')
    @patch('wp1.web.emails.ENV', 'test')
    @patch('wp1.web.emails.jinja_env')
    def test_send_zim_ready_email_request_exception(self, mock_jinja_env, mock_credentials, mock_post):
        """Test email sending when request raises an exception."""
        mock_credentials.get.return_value = {
            'MAILGUN': {
                'api_key': 'test-api-key',
                'url': 'https://api.mailgun.net/v3/test.com/messages'
            }
        }
        
        mock_template = Mock()
        mock_template.render.return_value = '<html>Test email content</html>'
        mock_jinja_env.get_template.return_value = mock_template
        
        mock_post.side_effect = Exception('Connection error')
        
        result = send_zim_ready_email(
            recipient_username='testuser',
            recipient_email='test@example.com',
            zim_title='Test ZIM',
            download_url='https://download.example.com/test.zim'
        )
        
        self.assertFalse(result)

    @patch('wp1.web.emails.send_zim_ready_email')
    @patch('wp1.web.emails.zim_schedules.get_username_by_zim_schedule_id')
    @patch('wp1.web.emails.zimfarm.zim_file_url_for_task_id')
    @patch('wp1.web.emails.zim_files.get_zim_file')
    @patch('wp1.web.emails.zim_schedules.decrement_remaining_generations')
    def test_notify_user_for_scheduled_zim(self, mock_decrement, mock_get_zim_file,
                                                   mock_zimfile_url, mock_get_username, mock_send_email):
        """Test successful user notification for scheduled ZIM."""
        mock_get_zim_file.return_value = self.mock_zim_file
        mock_zimfile_url.return_value = 'https://download.example.com/test.zim'
        mock_get_username.return_value = 'testuser'
        mock_send_email.return_value = True
        
        notify_user_for_scheduled_zim(self.wp10db, self.mock_zim_schedule)
        
        mock_decrement.assert_called_once_with(self.wp10db, self.mock_zim_schedule.s_id)
        mock_get_zim_file.assert_called_once_with(self.wp10db, self.mock_zim_schedule.s_zim_file_id)
        mock_zimfile_url.assert_called_once_with(self.mock_zim_file.z_task_id)
        mock_get_username.assert_called_once_with(self.wp10db, self.mock_zim_schedule.s_id)
        
        mock_send_email.assert_called_once_with(
            user_username='testuser',
            user_email='test@example.com',
            zim_title='Test ZIM File',
            download_url='https://download.example.com/test.zim',
            next_generation_months=3
        )

    @patch('wp1.web.emails.send_zim_ready_email')
    @patch('wp1.web.emails.zim_schedules.get_username_by_zim_schedule_id')
    @patch('wp1.web.emails.zimfarm.zim_file_url_for_task_id')
    @patch('wp1.web.emails.zim_files.get_zim_file')
    @patch('wp1.web.emails.zim_schedules.decrement_remaining_generations')
    def test_notify_user_for_scheduled_zim_no_remaining_generations(self, mock_decrement, mock_get_zim_file,
                                                                   mock_zimfile_url, mock_get_username, mock_send_email):
        """Test user notification when no remaining generations."""
        schedule_no_generations = ZimSchedule(
            s_id=str(uuid.uuid4()).encode('utf-8'),
            s_builder_id=b'test-builder-id',
            s_zim_file_id=b'test-zim-file-id',
            s_email=b'test@example.com',
            s_rq_job_id=b'test-job-id',
            s_last_updated_at=utcnow().strftime(TS_FORMAT_WP10).encode('utf-8'),
            s_interval=3,
            s_remaining_generations=0  # No remaining generations
        )
        
        mock_get_zim_file.return_value = self.mock_zim_file
        mock_zimfile_url.return_value = 'https://download.example.com/test.zim'
        mock_get_username.return_value = 'testuser'
        mock_send_email.return_value = True
        
        notify_user_for_scheduled_zim(self.wp10db, schedule_no_generations)
        
        mock_send_email.assert_called_once_with(
            user_username='testuser',
            user_email='test@example.com',
            zim_title='Test ZIM File',
            download_url='https://download.example.com/test.zim',
            next_generation_months=None  # Should be None when no remaining generations
        )

    @patch('wp1.web.emails.send_zim_ready_email')
    @patch('wp1.web.emails.zim_schedules.get_username_by_zim_schedule_id')
    @patch('wp1.web.emails.zimfarm.zim_file_url_for_task_id')
    @patch('wp1.web.emails.zim_files.get_zim_file')
    @patch('wp1.web.emails.zim_schedules.decrement_remaining_generations')
    def test_notify_user_for_scheduled_zim_no_title(self, mock_decrement, mock_get_zim_file,
                                                   mock_zimfile_url, mock_get_username, mock_send_email):
        """Test user notification when ZIM file has no title."""
        zim_file_no_title = ZimFile(
            z_id=b'test-zim-id',
            z_selection_id=b'test-selection-id',
            z_status=b'COMPLETED',
            z_task_id=b'test-task-id',
            z_title=None,  # No title
            z_description=b'Test description',
            z_long_description=b'Test long description'
        )
        
        mock_get_zim_file.return_value = zim_file_no_title
        mock_zimfile_url.return_value = 'https://download.example.com/test.zim'
        mock_get_username.return_value = 'testuser'
        mock_send_email.return_value = True
        
        notify_user_for_scheduled_zim(self.wp10db, self.mock_zim_schedule)
        
        mock_send_email.assert_called_once_with(
            user_username='testuser',
            user_email='test@example.com',
            zim_title='Your ZIM File',  # Should use default title
            download_url='https://download.example.com/test.zim',
            next_generation_months=3
        )
