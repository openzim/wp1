import uuid
from itsdangerous import URLSafeSerializer

from wp1.base_db_test import BaseWpOneDbTest
from wp1.web.app import create_app
from wp1.logic import zim_schedules
from wp1.models.wp10.zim_schedule import ZimSchedule
from wp1.constants import TS_FORMAT_WP10
from wp1.timestamp import utcnow
from wp1.config import get_settings, override_settings


class ZimEmailsEndpointsTest(BaseWpOneDbTest):

    def setUp(self):
        super().setUp()
        self.app = create_app()
        self.token = zim_schedules.generate_email_confirmation_token()
        self.schedule_id = str(uuid.uuid4()).encode("utf-8")

        self.zim_schedule = ZimSchedule(
            s_id=self.schedule_id,
            s_builder_id=str(uuid.uuid4()).encode("utf-8"),
            s_rq_job_id=b"test-job-id",
            s_last_updated_at=utcnow().strftime(TS_FORMAT_WP10).encode("utf-8"),
            s_interval=3,
            s_remaining_generations=5,
            s_email=b"test@example.com",
            s_title=b"Test ZIM Schedule",
            s_description=b"Test description",
            s_long_description=b"Test long description",
            s_email_confirmation_token=self.token,
        )

    def test_confirm_email_success(self):
        """Test successful email confirmation."""
        # Insert schedule with token
        zim_schedules.insert_zim_schedule(self.wp10db, self.zim_schedule)

        with self.app.test_client() as client:
            response = client.get(
                f'/v1/zim/confirm-email?token={self.token.decode("utf-8")}'
            )

            self.assertEqual(200, response.status_code)
            self.assertIn(b"Email Confirmed Successfully", response.data)
            self.assertIn(b"Test ZIM Schedule", response.data)

        # Verify token was removed
        fetched = zim_schedules.get_zim_schedule(self.wp10db, self.schedule_id)
        self.assertIsNone(fetched.s_email_confirmation_token)
        self.assertEqual(b"test@example.com", fetched.s_email)

    def test_confirm_email_missing_token(self):
        """Test email confirmation with missing token."""
        with self.app.test_client() as client:
            response = client.get("/v1/zim/confirm-email")

            self.assertEqual(400, response.status_code)
            self.assertIn(b"Invalid Confirmation Link", response.data)

    def test_confirm_email_invalid_token(self):
        """Test email confirmation with invalid token."""
        with self.app.test_client() as client:
            response = client.get("/v1/zim/confirm-email?token=invalid-token")

            self.assertEqual(404, response.status_code)
            self.assertIn(b"Invalid or Expired Confirmation Link", response.data)

    def test_confirm_email_already_confirmed(self):
        """Test email confirmation with already used token."""
        # Insert schedule and confirm once
        zim_schedules.insert_zim_schedule(self.wp10db, self.zim_schedule)
        zim_schedules.confirm_email_subscription(
            self.wp10db, self.token, b"test@example.com"
        )

        with self.app.test_client() as client:
            response = client.get(
                f'/v1/zim/confirm-email?token={self.token.decode("utf-8")}'
            )

            self.assertEqual(404, response.status_code)
            self.assertIn(b"Invalid or Expired Confirmation Link", response.data)

    def test_unsubscribe_email_success(self):
        """Test successful email unsubscribe."""
        # Insert schedule with token
        zim_schedules.insert_zim_schedule(self.wp10db, self.zim_schedule)

        with self.app.test_client() as client:
            response = client.get(
                f'/v1/zim/unsubscribe-email?token={self.token.decode("utf-8")}'
            )

            self.assertEqual(200, response.status_code)
            self.assertIn(b"Successfully Unsubscribed", response.data)
            self.assertIn(b"Test ZIM Schedule", response.data)

        # Verify both email and token were removed
        fetched = zim_schedules.get_zim_schedule(self.wp10db, self.schedule_id)
        self.assertIsNone(fetched.s_email_confirmation_token)
        self.assertIsNone(fetched.s_email)

    def test_unsubscribe_email_missing_token(self):
        """Test email unsubscribe with missing token."""
        with self.app.test_client() as client:
            response = client.get("/v1/zim/unsubscribe-email")

            self.assertEqual(400, response.status_code)
            self.assertIn(b"Invalid Unsubscribe Link", response.data)

    def test_unsubscribe_email_invalid_token(self):
        """Test email unsubscribe with invalid token."""
        with self.app.test_client() as client:
            response = client.get("/v1/zim/unsubscribe-email?token=invalid-token")

            self.assertEqual(404, response.status_code)
            self.assertIn(b"Invalid or Expired Unsubscribe Link", response.data)

    def test_unsubscribe_email_already_unsubscribed(self):
        """Test email unsubscribe with already used token."""
        # Insert schedule and unsubscribe once
        zim_schedules.insert_zim_schedule(self.wp10db, self.zim_schedule)
        zim_schedules.unsubscribe_email(self.wp10db, self.token)

        with self.app.test_client() as client:
            response = client.get(
                f'/v1/zim/unsubscribe-email?token={self.token.decode("utf-8")}'
            )

            self.assertEqual(404, response.status_code)
            self.assertIn(b"Invalid or Expired Unsubscribe Link", response.data)

    def test_unsubscribe_notification_success_without_session(self):
        self.zim_schedule.s_email_confirmation_token = None
        zim_schedules.insert_zim_schedule(self.wp10db, self.zim_schedule)
        token = zim_schedules.generate_notification_unsubscribe_token(self.zim_schedule)

        with self.app.test_client() as client:
            response = client.get(
                "/v1/zim/unsubscribe-notification", query_string={"token": token}
            )
            self.assertEqual(200, response.status_code)
            repeated = client.get(
                "/v1/zim/unsubscribe-notification", query_string={"token": token}
            )
            self.assertEqual(404, repeated.status_code)
        fetched = zim_schedules.get_zim_schedule(self.wp10db, self.schedule_id)
        self.assertIsNone(fetched.s_email)

    def test_unsubscribe_notification_invalid_capabilities_do_not_mutate(self):
        zim_schedules.insert_zim_schedule(self.wp10db, self.zim_schedule)
        token = zim_schedules.generate_notification_unsubscribe_token(self.zim_schedule)
        wrong_recipient = ZimSchedule(
            s_id=self.schedule_id,
            s_builder_id=self.zim_schedule.s_builder_id,
            s_email=b"someone-else@example.com",
            s_last_updated_at=self.zim_schedule.s_last_updated_at,
        )
        serializer = URLSafeSerializer(
            get_settings().SESSION_SECRET_KEY, salt="zim-notification-unsubscribe-v1"
        )
        invalid_queries = (
            {},
            {"schedule_id": self.schedule_id.decode("utf-8")},
            {"token": self.schedule_id.decode("utf-8")},
            {"token": "invalid-token"},
            {"token": token + "tampered"},
            {"token": self.token.decode("utf-8")},
            {
                "token": zim_schedules.generate_notification_unsubscribe_token(
                    wrong_recipient
                )
            },
            {"token": serializer.dumps(["not", "a", "mapping"])},
            {
                "token": serializer.dumps(
                    {"schedule_id": [], "email": "test@example.com"}
                )
            },
            {
                "token": serializer.dumps(
                    {"schedule_id": self.schedule_id.decode("utf-8")}
                )
            },
            {
                "token": URLSafeSerializer(get_settings().SESSION_SECRET_KEY).dumps(
                    {
                        "schedule_id": self.schedule_id.decode("utf-8"),
                        "email": "test@example.com",
                    }
                )
            },
        )
        with self.app.test_client() as client:
            for query in invalid_queries:
                with self.subTest(query=query):
                    response = client.get(
                        "/v1/zim/unsubscribe-notification", query_string=query
                    )
                    self.assertIn(response.status_code, (400, 404))
                    fetched = zim_schedules.get_zim_schedule(
                        self.wp10db, self.schedule_id
                    )
                    self.assertEqual(self.zim_schedule.s_email, fetched.s_email)
                    self.assertEqual(self.token, fetched.s_email_confirmation_token)

    def test_unsubscribe_notification_stale_recipient_and_rotated_key(self):
        token = zim_schedules.generate_notification_unsubscribe_token(self.zim_schedule)
        self.zim_schedule.s_email = b"new-recipient@example.com"
        zim_schedules.insert_zim_schedule(self.wp10db, self.zim_schedule)
        with self.app.test_client() as client:
            response = client.get(
                "/v1/zim/unsubscribe-notification", query_string={"token": token}
            )
            self.assertEqual(404, response.status_code)
            current_token = zim_schedules.generate_notification_unsubscribe_token(
                self.zim_schedule
            )
            with override_settings(SESSION_SECRET_KEY="rotated-key"):
                response = client.get(
                    "/v1/zim/unsubscribe-notification",
                    query_string={"token": current_token},
                )
            self.assertEqual(404, response.status_code)
        fetched = zim_schedules.get_zim_schedule(self.wp10db, self.schedule_id)
        self.assertEqual(b"new-recipient@example.com", fetched.s_email)
