from unittest.mock import MagicMock, Mock, patch, ANY
import uuid

from wp1.base_db_test import BaseWpOneDbTest
from wp1.web.emails import send_zim_ready_email, respond_to_zim_task_completed
from wp1.models.wp10.zim_schedule import ZimSchedule
from wp1.models.wp10.zim_file import ZimTask
from wp1.constants import TS_FORMAT_WP10
from wp1.timestamp import utcnow


class EmailsTest(BaseWpOneDbTest):

    def setUp(self):
        super().setUp()
        self.zim_task = ZimTask(
            z_id=1234578,
            z_selection_id=b'test-selection-id',
            z_zim_schedule_id=b'schedule_123',
            z_status=b'COMPLETED',
            z_task_id=b'test-task-id',
        )
        
        self.zim_schedule = ZimSchedule(
            s_id=str(uuid.uuid4()).encode('utf-8'),
            s_builder_id=b'test-builder-id',
            s_email=b'test@example.com',
            s_rq_job_id=b'test-job-id',
            s_last_updated_at=utcnow().strftime(TS_FORMAT_WP10).encode('utf-8'),
            s_interval=3,
            s_remaining_generations=2,
            s_title=b'Test ZIM File',
            s_description=b'Test description',
            s_long_description=b'Test long description',
            s_email_confirmation_token=None  # Confirmed email
        )

        with self.wp10db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO zim_tasks (z_id, z_selection_id, z_zim_schedule_id, z_status, z_task_id)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    self.zim_task.z_id,
                    self.zim_task.z_selection_id,
                    self.zim_task.z_zim_schedule_id,
                    self.zim_task.z_status,
                    self.zim_task.z_task_id,
                )
            )
            cursor.execute(
                """
                INSERT INTO zim_schedules (
                    s_id, s_builder_id, s_email, s_rq_job_id, s_last_updated_at,
                    s_interval, s_remaining_generations, s_title, s_description, s_long_description
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    self.zim_schedule.s_id,
                    self.zim_schedule.s_builder_id,
                    self.zim_schedule.s_email,
                    self.zim_schedule.s_rq_job_id,
                    self.zim_schedule.s_last_updated_at,
                    self.zim_schedule.s_interval,
                    self.zim_schedule.s_remaining_generations,
                    self.zim_schedule.s_title,
                    self.zim_schedule.s_description,
                    self.zim_schedule.s_long_description,
                )
            )
        self.wp10db.commit()

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
    @patch('wp1.zimfarm.requests.get')
    def test_respond_to_zim_task_completed(self,
                                           patched_get,
                                           mock_get_username,
                                           mock_send_email):
        """Test successful user notification for scheduled ZIM."""
        resp = MagicMock()
        resp.json.return_value = {
            'config': {
                'warehouse_path': '/wikipedia'
            },
            'files': {
                'foo.zim': {
                    'name': 'foo.zim'
                }
            }
        }
        patched_get.return_value = resp
        mock_get_username.return_value = 'testuser'
        mock_send_email.return_value = True

        respond_to_zim_task_completed(self.wp10db, self.zim_task, self.zim_schedule)

        with self.wp10db.cursor() as cursor:
            cursor.execute(
                "SELECT s_remaining_generations FROM zim_schedules WHERE s_id = %s",
                (self.zim_schedule.s_id,)
            )
            row = cursor.fetchone()
            self.assertEqual(1, row['s_remaining_generations'])  

        mock_get_username.assert_called_once_with(self.wp10db, self.zim_schedule.s_id)
        mock_send_email.assert_called_once_with(
            recipient_username='testuser',
            recipient_email='test@example.com',
            zim_title='Test ZIM File',
            download_url='https://fake.wasabisys.com/org-kiwix-zimit/wikipedia/foo.zim',
            unsubscribe_url=ANY,
            next_generation_months=3
        )

    @patch('wp1.web.emails.send_zim_ready_email')
    @patch('wp1.web.emails.zim_schedules.get_username_by_zim_schedule_id')
    @patch('wp1.web.emails.zimfarm.zim_file_url_for_task_id')
    @patch('wp1.web.emails.zim_schedules.decrement_remaining_generations')
    def test_respond_to_zim_task_completed_no_remaining_generations(self,
                                                                    mock_decrement,
                                                                    mock_zimfile_url,
                                                                    mock_get_username,
                                                                    mock_send_email):
        """Test user notification when no remaining generations."""
        schedule_no_generations = ZimSchedule(
            s_id=str(uuid.uuid4()).encode('utf-8'),
            s_builder_id=b'test-builder-id',
            s_email=b'test@example.com',
            s_rq_job_id=b'test-job-id',
            s_last_updated_at=utcnow().strftime(TS_FORMAT_WP10).encode('utf-8'),
            s_interval=3,
            s_remaining_generations=0 ,  # No remaining generations
            s_title=b'Test ZIM File',
            s_description=b'Test description',
            s_long_description=b'Test long description'
        )

        mock_zimfile_url.return_value = 'https://download.example.com/test.zim'
        mock_get_username.return_value = 'testuser'
        mock_send_email.return_value = True

        respond_to_zim_task_completed(self.wp10db, self.zim_task, schedule_no_generations)

        mock_send_email.assert_called_once_with(
            recipient_username='testuser',
            recipient_email='test@example.com',
            zim_title='Test ZIM File',
            download_url='https://download.example.com/test.zim',
            unsubscribe_url=ANY,
            next_generation_months=None  # Should be None when no remaining generations
        )

    @patch('wp1.web.emails.send_zim_ready_email')
    @patch('wp1.web.emails.zim_schedules.get_username_by_zim_schedule_id')
    @patch('wp1.web.emails.zimfarm.zim_file_url_for_task_id')
    @patch('wp1.web.emails.zim_schedules.decrement_remaining_generations')
    def test_respond_to_zim_task_completed_no_title(self, mock_decrement, mock_zimfile_url,
                                                    mock_get_username, mock_send_email):
        """Test user notification when ZIM file has no title."""
        zim_schedule_no_title = ZimSchedule(
            s_id=b'test-schedule-id',
            s_builder_id=b'test-builder-id',
            s_email=b'test@example.com',
            s_rq_job_id=b'test-job-id',
            s_last_updated_at=utcnow().strftime(TS_FORMAT_WP10).encode('utf-8'),
            s_interval=3,
            s_remaining_generations=3
        )

        mock_zimfile_url.return_value = 'https://download.example.com/test.zim'
        mock_get_username.return_value = 'testuser'
        mock_send_email.return_value = True

        respond_to_zim_task_completed(self.wp10db, self.zim_task, zim_schedule_no_title)

        mock_send_email.assert_called_once_with(
            recipient_username='testuser',
            recipient_email='test@example.com',
            zim_title='Your ZIM File',  # Should use default title
            download_url='https://download.example.com/test.zim',
            unsubscribe_url='https://wp1.openzim.org/api/v1/zim/unsubscribe-notification?schedule_id=test-schedule-id',
            next_generation_months=3
        )

    @patch('wp1.web.emails.send_zim_ready_email')
    @patch('wp1.web.emails.zim_schedules.get_username_by_zim_schedule_id')
    @patch('wp1.zimfarm.requests.get')
    def test_respond_to_zim_task_completed_includes_unsubscribe_url(self,
                                                                    patched_get,
                                                                    mock_get_username,
                                                                    mock_send_email):
        """Test that notification emails include unsubscribe URL."""
        resp = MagicMock()
        resp.json.return_value = {
            'config': {
                'warehouse_path': '/wikipedia'
            },
            'files': {
                'foo.zim': {
                    'name': 'foo.zim'
                }
            }
        }
        patched_get.return_value = resp
        mock_get_username.return_value = 'testuser'
        mock_send_email.return_value = True

        respond_to_zim_task_completed(self.wp10db, self.zim_task, self.zim_schedule)

        call_args = mock_send_email.call_args
        call_kwargs = call_args.kwargs
        
        self.assertIn('unsubscribe_url', call_kwargs)
        unsubscribe_url = call_kwargs['unsubscribe_url']
        self.assertIsNotNone(unsubscribe_url)
        self.assertIn('unsubscribe-notification', unsubscribe_url)
        self.assertIn(f"schedule_id={self.zim_schedule.s_id.decode('utf-8')}", unsubscribe_url)
