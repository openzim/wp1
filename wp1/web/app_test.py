from base64 import b64encode
import json
import os
import unittest
from unittest.mock import patch

import fakeredis

from wp1.config import override_settings
from wp1.environment import Environment
from wp1.web.app import create_app
from wp1.web.base_web_testcase import BaseWebTestcase


class AppTest(BaseWebTestcase):

    def test_index(self):
        with self.override_db(self.app), self.app.test_client() as client:
            rv = client.get("/")
            self.assertTrue(b"<title>WP 1.0 API</title>" in rv.data)

    def test_swagger_yml(self):
        with self.override_db(self.app), self.app.test_client() as client:
            rv = client.get("/v1/openapi.yml")
            self.assertTrue(b"title: 'WP 1.0 Frontend'" in rv.data)

    def test_http_errors_return_json_body(self):
        with self.override_db(self.app), self.app.test_client() as client:
            rv = client.get("/v1/no/such/endpoint")
            self.assertEqual("404 NOT FOUND", rv.status)
            data = rv.get_json()
            self.assertIsNotNone(data)
            self.assertIn("error", data)


class SessionOriginTest(unittest.TestCase):
    """Use real routes and sessions, without the legacy client's Origin default."""

    ORIGIN = "https://wp1.example.com"

    def setUp(self):
        settings = override_settings(ENV=Environment.TEST, CLIENT_DOMAINS=[self.ORIGIN])
        settings.__enter__()
        self.addCleanup(settings.__exit__, None, None, None)
        redis_patch = patch(
            "wp1.web.app.redis.from_url", return_value=fakeredis.FakeStrictRedis()
        )
        redis_patch.start()
        self.addCleanup(redis_patch.stop)
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.assertNotIn("HTTP_ORIGIN", self.client.environ_base)
        self.login()

    def login(self):
        with self.client.session_transaction() as session:
            session["user"] = {"identity": {"username": "victim", "sub": "1234"}}

    def assert_logged_in(self):
        response = self.client.get("/v1/oauth/identify")
        self.assertEqual(200, response.status_code)
        self.assertEqual({"username": "victim"}, response.get_json())

    def test_untrusted_same_site_requests_cannot_mutate(self):
        for method, path in (
            ("POST", "/v1/builders/"),
            ("POST", "/v1/builders/victim-builder"),
            ("POST", "/v1/builders/victim-builder/delete"),
            ("POST", "/v1/builders/victim-builder/zim"),
            ("DELETE", "/v1/builders/victim-builder/schedule"),
            ("POST", "/v1/projects/Victim/update"),
            ("POST", "/v1/oauth/logout"),
        ):
            with self.subTest(method=method, path=path):
                response = self.client.open(
                    path,
                    method=method,
                    headers={"Origin": "https://untrusted.example.com"},
                    data={},
                )
                self.assertEqual(403, response.status_code)
                self.assertNotIn("Access-Control-Allow-Origin", response.headers)
                self.assert_logged_in()

    def test_missing_or_invalid_origin_cannot_log_out(self):
        for headers in (
            {},
            {"Origin": ""},
            {"Origin": "null"},
            {"Origin": self.ORIGIN + "/"},
            {"Origin": self.ORIGIN + "?"},
            {"Origin": "https://user@wp1.example.com"},
            {"Origin": self.ORIGIN + ".evil"},
            {"Origin": self.ORIGIN + ", https://evil.example"},
            {"Origin": "null", "Referer": self.ORIGIN + "/account"},
            {"Origin": "", "Referer": self.ORIGIN + "/account"},
            {
                "Origin": "https://untrusted.example.com",
                "Referer": self.ORIGIN + "/account",
            },
            {"Referer": "https://wp1.example.com.evil/account"},
            {"Referer": "https://wp1.example.com@evil.example/account"},
            {"Referer": "//wp1.example.com/account"},
            {"Referer": self.ORIGIN + "/account#fragment"},
            {"Referer": self.ORIGIN + "\\@evil.example/account"},
        ):
            with self.subTest(headers=headers):
                response = self.client.post("/v1/oauth/logout", headers=headers)
                self.assertEqual(403, response.status_code)
                self.assert_logged_in()

    def test_trusted_origin_logs_out_with_credentialed_cors(self):
        response = self.client.post(
            "/v1/oauth/logout",
            headers={"Origin": self.ORIGIN, "Referer": "https://untrusted.example/"},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.ORIGIN, response.headers["Access-Control-Allow-Origin"])
        self.assertEqual("true", response.headers["Access-Control-Allow-Credentials"])
        self.assertEqual(401, self.client.get("/v1/oauth/identify").status_code)

    def test_referer_fallback_logs_out_only_when_origin_absent(self):
        response = self.client.post(
            "/v1/oauth/logout",
            headers={"Referer": self.ORIGIN + "/account?tab=settings"},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(401, self.client.get("/v1/oauth/identify").status_code)

    def test_get_logout_does_not_change_session(self):
        response = self.client.get("/v1/oauth/logout")
        self.assertEqual(405, response.status_code)
        self.assert_logged_in()

    def test_oauth_get_handshake_does_not_require_origin(self):
        with override_settings(CLIENT_HOMEPAGE=self.ORIGIN + "/"):
            response = self.client.get("/v1/oauth/initiate")
        self.assertEqual(302, response.status_code)
        self.assertEqual(self.ORIGIN + "/", response.location)
        self.assert_logged_in()

    def test_cors_preflight_requires_exact_origin(self):
        for origin, accepted in (
            (self.ORIGIN, True),
            ("https://untrusted.example.com", False),
            ("https://wp1Xexample.com", False),
            (self.ORIGIN + ".evil", False),
            ("https://WP1.example.com", False),
            ("null", False),
        ):
            with self.subTest(origin=origin):
                response = self.client.options(
                    "/v1/oauth/logout",
                    headers={
                        "Origin": origin,
                        "Access-Control-Request-Method": "POST",
                    },
                )
                self.assertEqual(200, response.status_code)
                self.assertEqual(
                    origin if accepted else None,
                    response.headers.get("Access-Control-Allow-Origin"),
                )
        self.assert_logged_in()

    def test_ipv6_origin_is_literal_in_both_policies(self):
        origin = "http://[::1]:5173"
        with override_settings(CLIENT_DOMAINS=[origin]):
            client = create_app().test_client()
        with client.session_transaction() as session:
            session["user"] = {"identity": {"username": "victim", "sub": "1234"}}
        rejected = client.post(
            "/v1/oauth/logout", headers={"Origin": "http://[::2]:5173"}
        )
        self.assertEqual(403, rejected.status_code)
        self.assertNotIn("Access-Control-Allow-Origin", rejected.headers)
        accepted = client.post("/v1/oauth/logout", headers={"Origin": origin})
        self.assertEqual(200, accepted.status_code)
        self.assertEqual(origin, accepted.headers["Access-Control-Allow-Origin"])
        self.assertEqual(401, client.get("/v1/oauth/identify").status_code)

    def test_application_rejects_insecure_allowlist_overrides(self):
        for origins in ([], ["*"], ["https://*.example.com"], ["null"]):
            with self.subTest(origins=origins):
                with override_settings(CLIENT_DOMAINS=origins):
                    with self.assertRaisesRegex(RuntimeError, "CLIENT_DOMAINS"):
                        create_app()

    def test_public_project_reads_allow_any_origin_without_credentials(self):
        paths = (
            "/v1/projects/",
            "/v1/projects/count",
            "/v1/projects/assessments",
            "/v1/projects/Example",
            "/v1/projects/Example/table",
            "/v1/projects/Example/category_links",
            "/v1/projects/Example/category_links/sorted",
            "/v1/projects/Example/articles",
            "/v1/projects/Example/articles/random",
            "/v1/projects/Example/update/time",
            "/v1/projects/Example/update/progress",
        )
        for path in paths:
            with self.subTest(path=path):
                response = self.client.options(
                    path,
                    headers={
                        "Origin": "https://untrusted.example.com",
                        "Access-Control-Request-Method": "GET",
                    },
                )
                self.assertEqual(200, response.status_code)
                self.assertEqual("*", response.headers["Access-Control-Allow-Origin"])
                self.assertNotIn("Access-Control-Allow-Credentials", response.headers)
                self.assertEqual(
                    {"GET", "HEAD", "OPTIONS"},
                    set(response.headers["Access-Control-Allow-Methods"].split(", ")),
                )

    def test_public_project_errors_are_readable_cross_origin(self):
        with patch("wp1.web.projects.get_db"), patch(
            "wp1.web.projects.logic_project.get_project_by_name", return_value=None
        ):
            response = self.client.get(
                "/v1/projects/Unknown",
                headers={"Origin": "https://untrusted.example.com"},
            )
        self.assertEqual(404, response.status_code)
        self.assertEqual("*", response.headers["Access-Control-Allow-Origin"])
        self.assertNotIn("Access-Control-Allow-Credentials", response.headers)

    def test_project_update_preflight_remains_origin_restricted(self):
        for origin, accepted in (
            (self.ORIGIN, True),
            ("https://untrusted.example.com", False),
        ):
            with self.subTest(origin=origin):
                response = self.client.options(
                    "/v1/projects/Example/update",
                    headers={
                        "Origin": origin,
                        "Access-Control-Request-Method": "POST",
                    },
                )
                self.assertEqual(
                    origin if accepted else None,
                    response.headers.get("Access-Control-Allow-Origin"),
                )
                self.assertEqual(
                    "true" if accepted else None,
                    response.headers.get("Access-Control-Allow-Credentials"),
                )
