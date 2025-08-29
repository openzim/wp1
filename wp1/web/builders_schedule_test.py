import uuid
from unittest.mock import patch
import attr

from wp1.web.base_web_testcase import BaseWebTestcase
from wp1.logic.zim_schedules import insert_zim_schedule
from wp1.models.wp10.zim_schedule import ZimSchedule
from wp1.models.wp10.builder import Builder
from wp1.logic.builder import insert_builder
from wp1.timestamp import utcnow
from wp1.constants import TS_FORMAT_WP10


class BuildersScheduleTest(BaseWebTestcase):
    USER = {
        'access_token': 'access_token',
        'identity': {
            'username': 'WP1_user',
            'sub': '1234',
        },
    }
    def setUp(self):
        super().setUp()

        self.builder = Builder(b_id=b'1a-2b-3c-4d',
                               b_name=b'My Builder',
                               b_user_id='1234',
                               b_project=b'en.wikipedia.fake',
                               b_model=b'wp1.selection.models.simple',
                               b_params=b'{"list": ["a", "b", "c"]}',
                               b_created_at=b'20191225044444',
                               b_updated_at=b'20191225044444',
                               b_current_version=2,
                               b_selection_zim_version=2)

    def _insert_builder(self):
        with self.wp10db.cursor() as cursor:
            cursor.execute(
                '''INSERT INTO builders
                    (b_id, b_name, b_user_id, b_project, b_params, b_model,
                        b_created_at, b_updated_at, b_current_version,
                        b_selection_zim_version)
                    VALUES
                    (%(b_id)s, %(b_name)s, %(b_user_id)s, %(b_project)s,
                        %(b_params)s, %(b_model)s, %(b_created_at)s,
                        %(b_updated_at)s, %(b_current_version)s, %(b_selection_zim_version)s)
                ''', attr.asdict(self.builder))
        self.wp10db.commit()
        return self.builder.b_id.decode('utf-8')

    def _create_active_schedule(self):
        """Helper to create an active recurring schedule."""
        schedule = ZimSchedule(
            s_id=str(uuid.uuid4()).encode('utf-8'),
            s_builder_id=self.builder.b_id,
            s_rq_job_id=b'test-rq-job-id',
            s_last_updated_at=utcnow().strftime(TS_FORMAT_WP10).encode('utf-8'),
            s_interval=3,
            s_remaining_generations=5,
            s_long_description=b'Test schedule long description',
            s_description=b'Test schedule description',
            s_title=b'Test schedule title',
            s_email=b'test@example.com'
        )
        insert_zim_schedule(self.wp10db, schedule)
        return schedule

    def test_zim_status_includes_active_schedule(self):
        """Test that the ZIM status endpoint includes active schedule information."""
        # Create an active schedule
        self._insert_builder()
        schedule = self._create_active_schedule()

        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user'] = self.USER
            rv = client.get('/v1/builders/{}/zim/status'.format(self.builder.b_id.decode('utf-8')))

        self.assertEqual('200 OK', rv.status)
        data = rv.get_json()
        
        self.assertIsNotNone(data.get('active_schedule'))
        active_schedule = data['active_schedule']
        
        self.assertEqual(schedule.s_id.decode('utf-8'), active_schedule['schedule_id'])
        self.assertEqual(3, active_schedule['interval_months'])
        self.assertEqual(5, active_schedule['remaining_generations'])
        self.assertEqual('test@example.com', active_schedule['email'])

    def test_zim_status_no_active_schedule(self):
        """Test ZIM status when no active schedule exists."""
        self._insert_builder()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user'] = self.USER
            rv = client.get('/v1/builders/{}/zim/status'.format(self.builder.b_id.decode('utf-8')))
            
        self.assertEqual('200 OK', rv.status)
        data = rv.get_json()
        
        self.assertIsNone(data.get('active_schedule'))

    @patch('wp1.logic.zim_schedules.delete_zim_schedule')
    def test_delete_schedule_success(self, mock_delete):
        """Test successful deletion of an active schedule."""
        mock_delete.return_value = True
        
        # Create an active schedule
        self._insert_builder()
        self._create_active_schedule()
        
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user'] = self.USER
            rv = client.delete('/v1/builders/{}/schedule'.format(self.builder.b_id.decode('utf-8')))
            
        self.assertEqual('204 NO CONTENT', rv.status)
        mock_delete.assert_called_once()

    def test_delete_schedule_no_schedule(self):
        """Test deletion when no active schedule exists."""
        self._insert_builder()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user'] = self.USER
            rv = client.delete('/v1/builders/{}/schedule'.format(self.builder.b_id.decode('utf-8')))
            
        self.assertEqual('404 NOT FOUND', rv.status)
        data = rv.get_json()
        self.assertIn('No active recurring schedule found', data['error_messages'])

