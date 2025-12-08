import unittest
from unittest.mock import Mock, patch

from wp1.credentials import CREDENTIALS
from wp1.environment import Environment
from wp1.web.app import create_app
from wp1.web.base_web_testcase import BaseWebTestcase
from wp1.web.db import get_db

USER = {
    "access_token": "access_token",
    "identity": {"username": "WP1_user", "email": "wp1user@email.ch", "sub": "1234"},
}
REQUEST_TOKEN = {"key": "request_token", "secret": "request_token_secret"}
REDIRECT = (
    "https://en.wikipedia.org/w/index.php?oauth_token=token&oauth_consumer_key=key"
)
handshaker = Mock(
    **{
        "initiate.return_value": (REDIRECT, REQUEST_TOKEN),
        "complete.return_value": {"key": "access_token", "secret": "access_secret"},
        "identify.return_value": USER["identity"],
    }
)


class IdentifyTest(BaseWebTestcase):
    ENV = Environment.TEST
    TEST_OAUTH_CREDS = {
        Environment.TEST: {
            **CREDENTIALS[Environment.TEST],
            "API": {},
            "MWOAUTH": {
                "consumer_key": "consumer_key",
                "consumer_secret": "consumer_secret",
            },
            "SESSION": {"secret_key": "wp1_secret"},
            "CLIENT_URL": {
                "domain": "localhost:5173",
                "homepage": "http://localhost:5173/#/",
            },
        },
        Environment.PRODUCTION: {},
    }

    @patch("wp1.web.oauth.CREDENTIALS", TEST_OAUTH_CREDS)
    @patch("wp1.web.oauth.get_handshaker", lambda: handshaker)
    def test_initiate_authorized_user(self):
        self.app = create_app(session_type="filesystem")
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = USER
            rv = client.get("/v1/oauth/initiate")
            self.assertEqual("302 FOUND", rv.status)
            self.assertEqual("http://localhost:5173/#/", rv.location)

    @patch("wp1.web.oauth.CREDENTIALS", TEST_OAUTH_CREDS)
    @patch("wp1.web.oauth.get_handshaker", lambda: handshaker)
    def test_initiate_unauthorized_user(self):
        self.app = create_app()
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["request_token"] = REQUEST_TOKEN
            rv = client.get("/v1/oauth/initiate")
            self.assertEqual(REDIRECT, rv.location)

    @patch("wp1.web.oauth.CREDENTIALS", TEST_OAUTH_CREDS)
    def test_initiate_authorized_user_with_next_path(self):
        self.app = create_app()
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = USER
            rv = client.get("/v1/oauth/initiate?next=update")
            self.assertEqual("302 FOUND", rv.status)
            self.assertEqual(f"http://localhost:5173/#/update", rv.location)

    @patch("wp1.web.oauth.CREDENTIALS", TEST_OAUTH_CREDS)
    def test_complete_unauthorized_user(self):
        self.app = create_app()
        with self.app.test_client() as client:
            rv = client.get("/v1/oauth/complete")
            self.assertEqual("404 NOT FOUND", rv.status)

    @patch("wp1.web.oauth.CREDENTIALS", TEST_OAUTH_CREDS)
    @patch("wp1.web.oauth.get_handshaker", lambda: handshaker)
    def test_complete_authorized_user_email(self):
        self.app = create_app()
        user_id = USER["identity"]["sub"]
        with self.override_db(self.app), self.app.test_client() as client:
            with self.app.app_context():
                with self.wp10db.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO users (u_id, u_username, u_email) VALUES (%s, %s, %s)",
                        (user_id, "overwrite", "test@test.it"),
                    )
                    self.wp10db.commit()
            with client.session_transaction() as sess:
                sess["request_token"] = REQUEST_TOKEN
            client.get("/v1/oauth/complete?query_string")

            with self.wp10db.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE u_id = %s", (user_id))
                row = cursor.fetchone()
                self.assertIsNotNone(row)
                # should overwrite username and email
                self.assertEqual("WP1_user", row["u_username"].decode("utf-8"))
                self.assertEqual("wp1user@email.ch", row["u_email"].decode("utf-8"))

    @patch("wp1.web.oauth.CREDENTIALS", TEST_OAUTH_CREDS)
    @patch("wp1.web.oauth.get_handshaker", lambda: handshaker)
    def test_complete_authorized_user(self):
        self.app = create_app()
        user_id = USER["identity"]["sub"]
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["request_token"] = REQUEST_TOKEN
            client.get("/v1/oauth/complete?query_string")

            with self.wp10db.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE u_id = %s", (user_id))
                row = cursor.fetchone()
                self.assertIsNotNone(row)
                self.assertEqual("wp1user@email.ch", row["u_email"].decode("utf-8"))

    @patch("wp1.web.oauth.CREDENTIALS", TEST_OAUTH_CREDS)
    @patch("wp1.web.oauth.get_handshaker", lambda: handshaker)
    def test_complete_authorized_user_with_next_path(self):
        print(self.TEST_OAUTH_CREDS)
        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["request_token"] = REQUEST_TOKEN
                sess["next_path"] = "update"
            rv = client.get("/v1/oauth/complete?query_string")
            self.assertEqual("302 FOUND", rv.status)
            self.assertEqual(f"http://localhost:5173/#/update", rv.location)
            wp10db = get_db("wp10db")
            with wp10db.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE u_id = 1234")
                self.assertNotEqual(None, cursor.fetchone())

    @patch("wp1.web.oauth.CREDENTIALS", TEST_OAUTH_CREDS)
    def test_identify_authorized_user(self):
        self.app = create_app()
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = USER
            rv = client.get("/v1/oauth/identify")
            self.assertEqual({"username": "WP1_user"}, rv.get_json())

    @patch("wp1.web.oauth.CREDENTIALS", TEST_OAUTH_CREDS)
    def test_identify_unauthorized_user(self):
        self.app = create_app()
        with self.app.test_client() as client:
            rv = client.get("/v1/oauth/identify")
            self.assertEqual("401 UNAUTHORIZED", rv.status)

    @patch("wp1.web.oauth.CREDENTIALS", TEST_OAUTH_CREDS)
    def test_logout_authorized_user(self):
        self.app = create_app()
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = USER
                sess["next_path"] = "/"
            rv = client.get("/v1/oauth/logout")
            self.assertEqual({"status": "204"}, rv.get_json())

    @patch("wp1.web.oauth.CREDENTIALS", TEST_OAUTH_CREDS)
    def test_logout_unauthorized_user(self):
        self.app = create_app()
        with self.app.test_client() as client:
            rv = client.get("/v1/oauth/logout")
            self.assertEqual("404 NOT FOUND", rv.status)

    @patch("wp1.web.oauth.CREDENTIALS", TEST_OAUTH_CREDS)
    def test_email_unauthorized_user(self):
        self.app = create_app()
        with self.app.test_client() as client:
            rv = client.get("/v1/oauth/email")
            self.assertEqual("401 UNAUTHORIZED", rv.status)

    @patch("wp1.web.oauth.CREDENTIALS", TEST_OAUTH_CREDS)
    def test_email_authorized_user_with_email_in_session(self):
        self.app = create_app()
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = USER
            rv = client.get("/v1/oauth/email")
            self.assertEqual({"email": USER["identity"]["email"]}, rv.get_json())

    @patch("wp1.web.oauth.CREDENTIALS", TEST_OAUTH_CREDS)
    def test_email_authorized_user_without_session_exists_in_db(self):
        self.app = create_app()
        user_id = USER["identity"]["sub"]
        with self.override_db(self.app), self.app.test_client() as client:
            # seed database with an email
            with self.app.app_context():
                with self.wp10db.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO users (u_id, u_username, u_email) VALUES (%s, %s, %s)",
                        (user_id, "someuser", "dbemail@domain.com"),
                    )
                    self.wp10db.commit()
            with client.session_transaction() as sess:
                sess["user"] = {
                    "access_token": USER["access_token"],
                    "identity": {
                        "username": USER["identity"]["username"],
                        "sub": user_id,
                    },
                }
            rv = client.get("/v1/oauth/email")
            self.assertEqual({"email": "dbemail@domain.com"}, rv.get_json())

    @patch("wp1.web.oauth.CREDENTIALS", TEST_OAUTH_CREDS)
    def test_email_authorized_user_without_session_not_in_db(self):
        self.app = create_app()
        user_id = USER["identity"]["sub"]
        with self.override_db(self.app), self.app.test_client() as client:
            # do not insert any user row
            with client.session_transaction() as sess:
                sess["user"] = {
                    "access_token": USER["access_token"],
                    "identity": {
                        "username": USER["identity"]["username"],
                        "sub": user_id,
                    },
                }
            rv = client.get("/v1/oauth/email")
            self.assertEqual({"email": None}, rv.get_json())
