import datetime
from unittest.mock import ANY, MagicMock, patch

import attr

from wp1.exceptions import ZimFarmError
from wp1.models.wp10.builder import Builder
from wp1.models.wp10.zim_schedule import ZimSchedule
from wp1.web.app import create_app
from wp1.web.base_web_testcase import BaseWebTestcase
from wp1.zimfarm import (
    MAX_ZIMFARM_ARTICLE_COUNT,
    ZIM_DESCRIPTION_MAX_LENGTH,
    ZIM_LONG_DESCRIPTION_MAX_LENGTH,
    ZIM_TITLE_MAX_LENGTH,
)


class BuildersTest(BaseWebTestcase):
    USER = {
        "access_token": "access_token",
        "identity": {
            "username": "WP1_user",
            "sub": "1234",
        },
    }
    UNAUTHORIZED_USER = {
        "access_token": "access_token",
        "identity": {
            "username": "WP1_user_2",
            "sub": "5678",
        },
    }
    invalid_article_name = ["Eiffel_Tower", "Statue of#Liberty"]
    unsuccessful_response = {
        "success": False,
        "items": {
            "valid": ["Eiffel_Tower"],
            "invalid": ["Statue_of#Liberty"],
            "errors": ["The list contained the following invalid characters: #"],
        },
    }
    empty_response = {
        "success": False,
        "items": {
            "valid": [],
            "invalid": [],
            "errors": ["Empty List"],
        },
    }
    valid_article_name = ["Eiffel_Tower", "Statue of Liberty"]
    successful_response = {"success": True, "items": {}}

    builder = Builder(
        b_id=b"1a-2b-3c-4d",
        b_name=b"My Builder",
        b_user_id="1234",
        b_project=b"en.wikipedia.fake",
        b_model=b"wp1.selection.models.simple",
        b_params=b'{"list": ["a", "b", "c"]}',
        b_created_at=b"20191225044444",
        b_updated_at=b"20191225044444",
        b_current_version=2,
        b_selection_zim_version=2,
    )

    def _insert_builder(self):
        with self.wp10db.cursor() as cursor:
            cursor.execute(
                """INSERT INTO builders
               (b_id, b_name, b_user_id, b_project, b_params, b_model,
                b_created_at, b_updated_at, b_current_version,
                b_selection_zim_version)
             VALUES
               (%(b_id)s, %(b_name)s, %(b_user_id)s, %(b_project)s,
                %(b_params)s, %(b_model)s, %(b_created_at)s,
                %(b_updated_at)s, %(b_current_version)s, %(b_selection_zim_version)s)
        """,
                attr.asdict(self.builder),
            )
        self.wp10db.commit()
        return self.builder.b_id.decode("utf-8")

    def _insert_selections(self, builder_id):
        selections = [
            (
                1,
                builder_id,
                "text/tab-separated-values",
                "20201225105544",
                1,
                "object_key1",
            ),
            (
                2,
                builder_id,
                "application/vnd.ms-excel",
                "20201225105544",
                1,
                "object_key2",
            ),
            (
                3,
                builder_id,
                "text/tab-separated-values",
                "20201225105544",
                2,
                "latest_object_key_tsv",
                "task-id-1234",
                "FILE_READY",
                b"schedule_123",
            ),
            (
                4,
                builder_id,
                "application/vnd.ms-excel",
                "20201225105544",
                2,
                "latest_object_key_xls",
            ),
        ]
        with self.wp10db.cursor() as cursor:
            cursor.executemany(
                """INSERT INTO selections
               (s_id, s_builder_id, s_content_type, s_updated_at,
                s_version, s_object_key, s_article_count)
             VALUES (%s, %s, %s, %s, %s, %s, 1000)
      """,
                [s[:6] for s in selections],
            )
            cursor.execute(
                """INSERT INTO zim_tasks
               (z_id, z_selection_id, z_task_id, z_status, z_zim_schedule_id)
             VALUES
               (1, %s, %s, %s, %s)""",
                (
                    selections[2][0],
                    selections[2][6],
                    selections[2][7],
                    selections[2][8],
                ),
            )
        self.wp10db.commit()

    def _insert_zim_schedule(
        self,
        schedule_id=b"schedule_123",
        builder_id=b"1a-2b-3c-4d",
        rq_job_id=b"rq_job_id_123",
        last_updated_at="20191225044444",
        email=None,
        title=None,
        description=None,
        long_description=None,
        remaining_generations=3,
    ):
        with self.wp10db.cursor() as cursor:
            cursor.execute(
                """INSERT INTO zim_schedules (s_id, s_builder_id, s_rq_job_id, s_remaining_generations,
                                        s_last_updated_at, s_title, s_description, s_long_description, s_email)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
          """,
                (
                    schedule_id,
                    builder_id,
                    rq_job_id,
                    remaining_generations,
                    last_updated_at,
                    title,
                    description,
                    long_description,
                    email,
                ),
            )
        self.wp10db.commit()
        return schedule_id

    def test_get_builder(self):
        self.app = create_app()
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            builder_id = self._insert_builder()
            rv = client.get(f"/v1/builders/{builder_id}")

            self.assertEqual("200 OK", rv.status)

    def test_get_builder_not_found(self):
        self.app = create_app()
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            self._insert_builder()
            rv = client.get("/v1/builders/1234")

            self.assertEqual("404 NOT FOUND", rv.status)

    def test_get_builder_unauthorized(self):
        self.app = create_app()
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.UNAUTHORIZED_USER
            builder_id = self._insert_builder()
            rv = client.get(f"/v1/builders/{builder_id}")

            self.assertEqual("401 UNAUTHORIZED", rv.status)

    def test_create_unsuccessful(self):
        self.app = create_app()
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/",
                json={
                    "model": "wp1.selection.models.simple",
                    "params": {"list": self.invalid_article_name},
                    "name": "my_list",
                    "project": "my_project",
                },
            )
            self.assertEqual(self.unsuccessful_response, rv.get_json())

    def test_create_successful(self):
        self.app = create_app()
        with self.app.test_client() as client, self.override_db(self.app):
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/",
                json={
                    "model": "wp1.selection.models.simple",
                    "params": {"list": self.valid_article_name},
                    "name": "my_list",
                    "project": "my_project",
                },
            )

            with self.wp10db.cursor() as cursor:
                cursor.execute("SELECT b_id FROM builders WHERE b_name = 'my_list'")
                result = cursor.fetchone()

            db_id = result["b_id"].decode("utf-8")

            expected = {"success": True, "id": db_id, "items": {}}

            self.assertEqual(expected, rv.get_json())

    def test_create_throws(self):
        self.app = create_app()
        with self.app.test_client() as client, self.override_db(self.app):
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/",
                json={
                    "model": "fake_model",
                    "params": {"list": self.valid_article_name},
                    "name": "my_list",
                    "project": "my_project",
                },
            )
            self.assertEqual("400 BAD REQUEST", rv.status)

    def test_update_unsuccessful(self):
        builder_id = self._insert_builder()
        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/%s" % builder_id,
                json={
                    "model": "wp1.selection.models.simple",
                    "params": {"list": self.invalid_article_name},
                    "name": "updated_list",
                    "project": "my_project",
                },
            )
            self.assertEqual(self.unsuccessful_response, rv.get_json())

    def test_update_successful(self):
        builder_id = self._insert_builder()
        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/%s" % builder_id,
                json={
                    "model": "wp1.selection.models.simple",
                    "params": {"list": self.valid_article_name},
                    "name": "updated_list",
                    "project": "my_project",
                },
            )

            with self.wp10db.cursor() as cursor:
                cursor.execute(
                    "SELECT b_name FROM builders WHERE b_id = %s",
                    (builder_id.encode("utf-8"),),
                )
                result = cursor.fetchone()

            self.assertEqual(b"updated_list", result["b_name"])

            expected = {"success": True, "id": builder_id, "items": {}}

            self.assertEqual(expected, rv.get_json())

    def test_update_not_owner(self):
        builder_id = self._insert_builder()
        different_user = {
            "access_token": "access_token",
            "identity": {
                "username": "Another_User",
                "sub": 5555,
            },
        }
        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = different_user
            rv = client.post(
                "/v1/builders/%s" % builder_id,
                json={
                    "model": "wp1.selection.models.simple",
                    "params": {"list": self.valid_article_name},
                    "name": "updated_list",
                    "project": "my_project",
                },
            )
            self.assertEqual("404 NOT FOUND", rv.status)

    def test_empty_articles_create(self):
        self.app = create_app()
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/",
                json={
                    "model": "wp1.selection.models.simple",
                    "params": {"list": []},
                    "name": "my_list",
                    "project": "my_project",
                },
            )
            self.assertEqual(self.empty_response, rv.get_json())

    def test_empty_name_create(self):
        self.app = create_app()
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/",
                json={
                    "model": "wp1.selection.models.simple",
                    "params": {"list": self.valid_article_name},
                    "name": "",
                    "project": "my_project",
                },
            )
            self.assertEqual("400 BAD REQUEST", rv.status)

    def test_empty_project_create(self):
        self.app = create_app()
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/",
                json={
                    "model": "wp1.selection.models.simple",
                    "params": {"list": self.valid_article_name},
                    "name": "my_list",
                    "project": "",
                },
            )
            self.assertEqual("400 BAD REQUEST", rv.status)

    def test_selection_unauthorized_user_create(self):
        self.app = create_app()
        with self.app.test_client() as client:
            rv = client.post(
                "/v1/builders/",
                json={
                    "model": "wp1.selection.models.simple",
                    "articles": {"list": self.valid_article_name},
                    "name": "my_list",
                    "project": "my_project",
                },
            )
        self.assertEqual("401 UNAUTHORIZED", rv.status)

    def test_empty_articles_update(self):
        builder_id = self._insert_builder()
        self.app = create_app()
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/%s" % builder_id,
                json={
                    "model": "wp1.selection.models.simple",
                    "params": {"list": []},
                    "name": "my_list",
                    "project": "my_project",
                },
            )
            self.assertEqual(self.empty_response, rv.get_json())

    def test_empty_list_update(self):
        builder_id = self._insert_builder()
        self.app = create_app()
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/%s" % builder_id,
                json={
                    "model": "wp1.selection.models.simple",
                    "params": {"list": self.valid_article_name},
                    "name": "",
                    "project": "my_project",
                },
            )
            self.assertEqual("400 BAD REQUEST", rv.status)

    def test_empty_project_update(self):
        builder_id = self._insert_builder()
        self.app = create_app()
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/%s" % builder_id,
                json={
                    "model": "wp1.selection.models.simple",
                    "params": {"list": self.valid_article_name},
                    "name": "my_list",
                    "project": "",
                },
            )
            self.assertEqual("400 BAD REQUEST", rv.status)

    def test_selection_unauthorized_user_update(self):
        builder_id = self._insert_builder()
        self.app = create_app()
        with self.app.test_client() as client:
            rv = client.post(
                "/v1/builders/%s" % builder_id,
                json={
                    "model": "wp1.selection.models.simple",
                    "params": {"list": self.valid_article_name},
                    "name": "my_list",
                    "project": "my_project",
                },
            )
        self.assertEqual("401 UNAUTHORIZED", rv.status)

    def test_latest_selection(self):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)
        self.app = create_app()
        with self.app.test_client() as client:
            rv = client.get("/v1/builders/%s/selection/latest.tsv" % builder_id)
        self.assertEqual("302 FOUND", rv.status)
        self.assertEqual(
            "http://credentials.not.found.fake/latest_object_key_tsv",
            rv.headers["Location"],
        )

    def test_latest_selection_bad_content_type(self):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)
        self.app = create_app()
        with self.app.test_client() as client:
            rv = client.get("/v1/builders/%s/selection/latest.foo" % builder_id)
        self.assertEqual("404 NOT FOUND", rv.status)

    def test_latest_selection_bad_builder_id(self):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)
        self.app = create_app()
        with self.app.test_client() as client:
            rv = client.get("/v1/builders/-1/selection/latest.tsv")
        self.assertEqual("404 NOT FOUND", rv.status)

    def test_latest_selection_no_selections(self):
        builder_id = self._insert_builder()
        self.app = create_app()
        with self.app.test_client() as client:
            rv = client.get("/v1/builders/%s/selection/latest.tsv" % builder_id)
        self.assertEqual("404 NOT FOUND", rv.status)

    @patch("wp1.logic.builder.redis_connect")
    @patch("wp1.logic.selection.connect_storage")
    def test_delete_successful(self, patched_connect_storage, patched_redis_connect):
        patched_redis_connect.return_value = MagicMock()
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)
        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post("/v1/builders/%s/delete" % builder_id)
            self.assertEqual("200 OK", rv.status)
            self.assertEqual({"status": "204"}, rv.get_json())

    @patch("wp1.logic.builder.redis_connect")
    @patch("wp1.logic.selection.connect_storage")
    def test_delete_no_selections(self, patched_connect_storage, patched_redis_connect):
        patched_redis_connect.return_value = MagicMock()
        builder_id = self._insert_builder()

        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post("/v1/builders/%s/delete" % builder_id)
            self.assertEqual("200 OK", rv.status)
            self.assertEqual({"status": "204"}, rv.get_json())

    @patch("wp1.logic.builder.redis_connect")
    @patch("wp1.logic.selection.connect_storage")
    def test_delete_not_owner(self, patched_connect_storage, patched_redis_connect):
        patched_redis_connect.return_value = MagicMock()
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)
        different_user = {
            "access_token": "access_token",
            "identity": {
                "username": "Another_User",
                "sub": 5555,
            },
        }
        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = different_user
            rv = client.post("/v1/builders/%s/delete" % builder_id)
            self.assertEqual("403 FORBIDDEN", rv.status)

    @patch("wp1.logic.selection.connect_storage")
    @patch("wp1.logic.builder.redis_connect")
    def test_delete_no_builder(self, patched_redis_connect, patched_connect_storage):
        patched_redis_connect.return_value = MagicMock()
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)

        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post("/v1/builders/-1/delete")
            self.assertEqual("404 NOT FOUND", rv.status)

    @patch("wp1.zimfarm.request_zimfarm_task")
    @patch("wp1.zimfarm.create_or_update_zimfarm_schedule")
    def test_create_zim_file_for_builder(
        self, patched_create_zimfarm_schedule, patched_request_zimfarm_task
    ):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)

        patched_request_zimfarm_task.return_value = "1234-a"
        patched_create_zimfarm_schedule.return_value = ZimSchedule(
            s_id=b"schedule_123",
            s_builder_id=b"1a-2b-3c-4d",
            s_rq_job_id=b"rq_job_id_123",
            s_last_updated_at=b"20240101000000",
            s_email_confirmation_token=None,
        )

        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/%s/zim" % builder_id,
                json={"title": "Test title", "description": "Test description"},
            )
            self.assertEqual("204 NO CONTENT", rv.status)

        patched_request_zimfarm_task.assert_called_once()
        with self.wp10db.cursor() as cursor:
            cursor.execute(
                "SELECT z_task_id, z_status FROM zim_tasks " "WHERE z_selection_id = 3"
            )
            data = cursor.fetchone()

        self.assertEqual(b"1234-a", data["z_task_id"])
        self.assertEqual(b"REQUESTED", data["z_status"])

    @patch("wp1.zimfarm.request_zimfarm_task")
    @patch("wp1.zimfarm.create_or_update_zimfarm_schedule")
    def test_create_zim_file_for_builder_not_found(
        self, patched_create_zimfarm_schedule, patched_request_zimfarm_task
    ):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)

        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/1234-not-found/zim",
                json={"title": "Test title", "description": "Test description"},
            )
            self.assertEqual("404 NOT FOUND", rv.status)

    @patch("wp1.zimfarm.request_zimfarm_task")
    @patch("wp1.zimfarm.create_or_update_zimfarm_schedule")
    def test_create_zim_file_for_builder_unauthorized(
        self, patched_create_zimfarm_schedule, patched_request_zimfarm_task
    ):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)

        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.UNAUTHORIZED_USER
            rv = client.post(
                "/v1/builders/%s/zim" % builder_id,
                json={"title": "Test title", "description": "Test description"},
            )
            self.assertEqual("403 FORBIDDEN", rv.status)

    @patch("wp1.zimfarm.request_zimfarm_task")
    @patch("wp1.zimfarm.create_or_update_zimfarm_schedule")
    def test_create_zim_file_for_builder_500(
        self, patched_create_zimfarm_schedule, patched_request_zimfarm_task
    ):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)

        patched_request_zimfarm_task.side_effect = ZimFarmError

        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/%s/zim" % builder_id,
                json={"title": "Test title", "description": "Test description"},
            )
            self.assertEqual("500 INTERNAL SERVER ERROR", rv.status)

    @patch("wp1.zimfarm.request_zimfarm_task")
    def test_create_zim_file_for_builder_400(self, patched_request_zimfarm_task):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)

        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post("/v1/builders/%s/zim" % builder_id, json={})
            self.assertEqual("400 BAD REQUEST", rv.status)

    @patch("wp1.zimfarm.request_zimfarm_task")
    # Mock requests to avoid actual HTTP calls
    @patch("wp1.zimfarm.requests")
    @patch("wp1.zimfarm.get_zimfarm_token")
    def test_create_zim_file_for_builder_no_title(
        self, mock_get_token, mock_requests, mock_request_zimfarm_task
    ):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)

        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/%s/zim" % builder_id,
                json={"description": "Test description"},
            )
            self.assertEqual("400 BAD REQUEST", rv.status)

    @patch("wp1.zimfarm.request_zimfarm_task")
    # Mock requests to avoid actual HTTP calls
    @patch("wp1.zimfarm.requests")
    @patch("wp1.zimfarm.get_zimfarm_token")
    def test_create_zim_file_for_builder_too_long_title(
        self, mock_get_token, mock_requests, mock_request_zimfarm_task
    ):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)
        wrong_title = "a" * (ZIM_TITLE_MAX_LENGTH + 1)

        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/%s/zim" % builder_id,
                json={"title": wrong_title, "description": "Test description"},
            )
            self.assertEqual("400 BAD REQUEST", rv.status)

    @patch("wp1.zimfarm.request_zimfarm_task")
    # Mock requests to avoid actual HTTP calls
    @patch("wp1.zimfarm.requests")
    @patch("wp1.zimfarm.get_zimfarm_token")
    def test_create_zim_file_for_builder_too_long_description(
        self, mock_get_token, mock_requests, mock_request_zimfarm_task
    ):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)
        too_long_description = "z" * (ZIM_DESCRIPTION_MAX_LENGTH + 1)

        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/%s/zim" % builder_id,
                json={"title": "Test Title", "description": too_long_description},
            )
            self.assertEqual("400 BAD REQUEST", rv.status)

    @patch("wp1.zimfarm.request_zimfarm_task")
    # Mock requests to avoid actual HTTP calls
    @patch("wp1.zimfarm.requests")
    @patch("wp1.zimfarm.get_zimfarm_token")
    def test_create_zim_file_for_builder_too_long_long_description(
        self, mock_get_token, mock_requests, mock_request_zimfarm_task
    ):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)
        too_long_long_description = "z" * (ZIM_LONG_DESCRIPTION_MAX_LENGTH + 1)

        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/%s/zim" % builder_id,
                json={
                    "title": "Test Title",
                    "description": "Test Description",
                    "long_description": too_long_long_description,
                },
            )
            self.assertEqual("400 BAD REQUEST", rv.status)

    @patch("wp1.zimfarm.request_zimfarm_task")
    # Mock requests to avoid actual HTTP calls
    @patch("wp1.zimfarm.requests")
    @patch("wp1.zimfarm.get_zimfarm_token")
    def test_create_zim_file_for_builder_too_short_long_description(
        self, mock_get_token, mock_requests, mock_request_zimfarm_task
    ):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)

        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/%s/zim" % builder_id,
                json={
                    "title": "Test Title",
                    "description": "Test Description",
                    "long_description": "z",
                },
            )
            self.assertEqual("400 BAD REQUEST", rv.status)

    # Mock requests to avoid actual HTTP calls
    @patch("wp1.zimfarm.requests")
    @patch("wp1.zimfarm.get_zimfarm_token")
    def test_create_zim_file_for_builder_too_many_articles(
        self, token_mock, requests_mock
    ):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)
        with self.wp10db.cursor() as cursor:
            cursor.execute(
                "UPDATE selections SET s_article_count = %s",
                MAX_ZIMFARM_ARTICLE_COUNT + 100,
            )
        self.wp10db.commit()

        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/%s/zim" % builder_id,
                json={"description": "Test description"},
            )
            self.assertEqual("400 BAD REQUEST", rv.status)

    @patch("wp1.zimfarm.request_zimfarm_task")
    @patch("wp1.zimfarm.create_or_update_zimfarm_schedule")
    def test_create_zim_file_for_builder_scheduled_repetitions(
        self, patched_create_zimfarm_schedule, patched_request_zimfarm_task
    ):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)
        self._insert_zim_schedule(
            builder_id=b"1a-2b-3c-4d",
        )

        patched_request_zimfarm_task.return_value = "1234-a"
        patched_create_zimfarm_schedule.return_value = ZimSchedule(
            s_id=b"schedule_123",
            s_builder_id=b"1a-2b-3c-4d",
            s_rq_job_id=b"rq_job_id_123",
            s_last_updated_at=b"20240101000000",
            s_remaining_generations=3,
            s_email_confirmation_token=None,
        )

        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/%s/zim" % builder_id,
                json={
                    "title": "Test title",
                    "description": "Test description",
                    "scheduled_repetitions": {
                        "repetition_period_in_months": 6,
                        "number_of_repetitions": 3,
                        "email": "test@example.com",
                    },
                },
            )
            self.assertEqual("204 NO CONTENT", rv.status)

    @patch("wp1.zimfarm.request_zimfarm_task")
    @patch("wp1.zimfarm.create_or_update_zimfarm_schedule")
    def test_create_zim_file_for_builder_scheduled_repetitions_extra_fields(
        self, patched_create_zimfarm_schedule, patched_request_zimfarm_task
    ):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)
        self._insert_zim_schedule(
            builder_id=b"1a-2b-3c-4d",
        )

        patched_request_zimfarm_task.return_value = "1234-a"
        patched_create_zimfarm_schedule.return_value = ZimSchedule(
            s_id=b"schedule_123",
            s_builder_id=b"1a-2b-3c-4d",
            s_rq_job_id=b"rq_job_id_123",
            s_last_updated_at=b"20240101000000",
            s_remaining_generations=3,
            s_email_confirmation_token=None,
        )

        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/%s/zim" % builder_id,
                json={
                    "title": "Test title",
                    "description": "Test description",
                    "scheduled_repetitions": {
                        "repetition_period_in_months": 6,
                        "number_of_repetitions": 3,
                        "email": "test@example.com",
                        "extra_field": "should be ignored",
                    },
                },
            )
            self.assertEqual("204 NO CONTENT", rv.status)

    @patch("wp1.zimfarm.request_zimfarm_task")
    def test_create_zim_file_for_builder_scheduled_repetitions_missing_fields(
        self, patched_request_zimfarm_task
    ):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)

        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/%s/zim" % builder_id,
                json={
                    "title": "Test title",
                    "description": "Test description",
                    "scheduled_repetitions": {
                        "repetition_period_in_months": 6,
                        # Missing 'number_of_repetitions' field
                        "email": "user@example.com",
                    },
                },
            )
            self.assertEqual("400 BAD REQUEST", rv.status)
            self.assertIn(
                "Invalid or missing fields in scheduled_repetitions",
                rv.data.decode("utf-8"),
            )

    @patch("wp1.zimfarm.request_zimfarm_task")
    @patch("wp1.zimfarm.create_or_update_zimfarm_schedule")
    def test_create_zim_file_for_builder_scheduled_repetitions_not_dict(
        self, patched_create_zimfarm_schedule, patched_request_zimfarm_task
    ):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)

        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/%s/zim" % builder_id,
                json={
                    "title": "Test title",
                    "description": "Test description",
                    "scheduled_repetitions": "not a dict",
                },
            )
            self.assertEqual("400 BAD REQUEST", rv.status)
            self.assertIn(
                "Invalid or missing fields in scheduled_repetitions",
                rv.data.decode("utf-8"),
            )

    @patch("wp1.zimfarm.request_zimfarm_task")
    @patch("wp1.zimfarm.create_or_update_zimfarm_schedule")
    def test_create_zim_file_for_builder_scheduled_repetitions_empty_dict(
        self, patched_create_zimfarm_schedule, patched_request_zimfarm_task
    ):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)
        patched_create_zimfarm_schedule.return_value = ZimSchedule(
            s_id=b"schedule_123",
            s_builder_id=b"1a-2b-3c-4d",
            s_rq_job_id=b"rq_job_id_123",
            s_last_updated_at=b"20240101000000",
            s_email_confirmation_token=None,
        )

        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/%s/zim" % builder_id,
                json={
                    "title": "Test title",
                    "description": "Test description",
                    "scheduled_repetitions": {},
                },
            )
            # Expecting a 204 NO CONTENT response since the empty dict is treated as None
            self.assertEqual("204 NO CONTENT", rv.status)

    @patch("wp1.zimfarm.request_zimfarm_task")
    @patch("wp1.zimfarm.create_or_update_zimfarm_schedule")
    def test_create_zim_file_for_builder_scheduled_repetitions_extra_fields(
        self, patched_create_zimfarm_schedule, patched_request_zimfarm_task
    ):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)
        self._insert_zim_schedule(
            schedule_id=b"schedule_123",
            builder_id=builder_id.encode("utf-8"),
            rq_job_id=b"task-id-1234",
            last_updated_at="20221225000102",
        )
        patched_request_zimfarm_task.return_value = "1234-a"
        patched_create_zimfarm_schedule.return_value = ZimSchedule(
            s_id=b"schedule_123",
            s_builder_id=b"1a-2b-3c-4d",
            s_rq_job_id=b"rq_job_id_123",
            s_last_updated_at=b"20240101000000",
            s_email_confirmation_token=None,
        )

        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/%s/zim" % builder_id,
                json={
                    "title": "Test title",
                    "description": "Test description",
                    "scheduled_repetitions": {
                        "repetition_period_in_months": 6,
                        "number_of_repetitions": 3,
                        "email": "test@example.com",
                        "extra_field": "should be ignored",
                    },
                },
            )
            self.assertEqual("204 NO CONTENT", rv.status)

    @patch(
        "wp1.logic.selection.utcnow",
        return_value=datetime.datetime(2022, 12, 25, 0, 1, 2),
    )
    @patch("wp1.web.emails.notify_user_for_scheduled_zim")
    def test_update_zimfarm_status_file_scheduled(
        self, patched_notify_user, patched_utcnow
    ):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)
        self._insert_zim_schedule(
            schedule_id=b"schedule_123",
            builder_id=builder_id.encode("utf-8"),
            rq_job_id=b"task-id-1234",
            last_updated_at="20221225000102",
            remaining_generations=2,
            email="test@example.com",
        )
        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/zim/status?token=hook-token-abc",
                json={
                    "id": "task-id-1234",
                    "foo": "bar",
                    "status": "succeeded",
                    "files": {"zimfile.1234.zim": {"status": "uploaded"}},
                },
            )
            self.assertEqual("204 NO CONTENT", rv.status)

        with self.wp10db.cursor() as cursor:
            cursor.execute(
                "SELECT z_status, z_updated_at "
                'FROM zim_tasks WHERE z_task_id = "task-id-1234"'
            )
            status = cursor.fetchone()

        self.assertIsNotNone(status)
        self.assertEqual(b"FILE_READY", status["z_status"])
        self.assertEqual(b"20221225000102", status["z_updated_at"])
        patched_notify_user.assert_called_once()

    @patch(
        "wp1.logic.selection.utcnow",
        return_value=datetime.datetime(2022, 12, 25, 0, 1, 2),
    )
    @patch("wp1.web.emails.notify_user_for_scheduled_zim")
    def test_update_zimfarm_status_file_scheduled_no_email(
        self, patched_notify_user, patched_utcnow
    ):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)
        self._insert_zim_schedule(
            schedule_id=b"schedule_123",
            builder_id=builder_id.encode("utf-8"),
            rq_job_id=b"task-id-1234",
            last_updated_at="20221225000102",
            remaining_generations=2,
        )
        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/zim/status?token=hook-token-abc",
                json={
                    "id": "task-id-1234",
                    "foo": "bar",
                    "status": "succeeded",
                    "files": {"zimfile.1234.zim": {"status": "uploaded"}},
                },
            )
            self.assertEqual("204 NO CONTENT", rv.status)

        with self.wp10db.cursor() as cursor:
            cursor.execute(
                "SELECT z_status, z_updated_at "
                'FROM zim_tasks WHERE z_task_id = "task-id-1234"'
            )
            status = cursor.fetchone()

        self.assertIsNotNone(status)
        self.assertEqual(b"FILE_READY", status["z_status"])
        self.assertEqual(b"20221225000102", status["z_updated_at"])
        patched_notify_user.assert_not_called()

    @patch(
        "wp1.logic.selection.utcnow",
        return_value=datetime.datetime(2022, 12, 25, 0, 1, 2),
    )
    @patch("wp1.web.emails.respond_to_zim_task_completed")
    def test_update_zimfarm_status_file_missing_schedule(
        self, patched_utcnow, patched_notify_user
    ):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)
        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/zim/status?token=hook-token-abc",
                json={
                    "id": "task-id-1234",
                    "foo": "bar",
                    "status": "succeeded",
                    "files": {"zimfile.1234.zim": {"status": "uploaded"}},
                },
            )
            self.assertEqual("500 INTERNAL SERVER ERROR", rv.status)

    @patch(
        "wp1.logic.selection.utcnow",
        return_value=datetime.datetime(2022, 12, 25, 0, 1, 2),
    )
    def test_update_zimfarm_status_file_ready(self, patched_utcnow):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)
        self._insert_zim_schedule(
            schedule_id=b"schedule_123",
            builder_id=builder_id.encode("utf-8"),
            rq_job_id=b"task-id-1234",
            last_updated_at="20221225000102",
            remaining_generations=None,
        )
        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/zim/status?token=hook-token-abc",
                json={
                    "id": "task-id-1234",
                    "foo": "bar",
                    "status": "succeeded",
                    "files": {"zimfile.1234.zim": {"status": "uploaded"}},
                },
            )
            self.assertEqual("204 NO CONTENT", rv.status)

        with self.wp10db.cursor() as cursor:
            cursor.execute(
                "SELECT z_status, z_updated_at "
                'FROM zim_tasks WHERE z_task_id = "task-id-1234"'
            )
            status = cursor.fetchone()

        self.assertIsNotNone(status)
        self.assertEqual(b"FILE_READY", status["z_status"])
        self.assertEqual(b"20221225000102", status["z_updated_at"])

    def test_update_zimfarm_status_bad_token(self):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)
        self._insert_zim_schedule(
            schedule_id=b"schedule_123",
            builder_id=builder_id.encode("utf-8"),
            rq_job_id=b"task-id-1234",
            last_updated_at="20221225000102",
        )

        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/zim/status?token=foo-bad-token",
                json={"id": "task-id-1234", "foo": "bar"},
            )
            self.assertEqual("403 FORBIDDEN", rv.status)

    def test_update_zimfarm_status_invalid_payload(self):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)

        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/zim/status?token=hook-token-abc",
                json={"baz": "task-id-1234", "foo": "bar"},
            )
            self.assertEqual("400 BAD REQUEST", rv.status)

    def test_update_zimfarm_status_not_found_task_id(self):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)

        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/zim/status?token=hook-token-abc",
                json={"id": "task-id-not-found", "foo": "bar"},
            )
            self.assertEqual("204 NO CONTENT", rv.status)

    @patch(
        "wp1.logic.selection.utcnow",
        return_value=datetime.datetime(2022, 12, 25, 0, 1, 2),
    )
    def test_update_zimfarm_status_non_zim_file_uploaded(self, patched_utcnow):
        """Test that non-.zim files don't trigger FILE_READY status"""
        builder_id = self._insert_builder()

        with self.wp10db.cursor() as cursor:
            cursor.execute(
                """INSERT INTO selections
                   (s_id, s_builder_id, s_content_type, s_updated_at, s_version, s_object_key)
                 VALUES (1, %s, 'text/tab-separated-values', '20201225105544', 1, 'object_key')""",
                (builder_id,),
            )
            cursor.execute(
                """INSERT INTO zim_tasks
                   (z_id, z_selection_id, z_task_id, z_status, z_zim_schedule_id)
                 VALUES (1, 1, 'task-id-non-zim', 'REQUESTED', 'schedule_456')"""
            )

        self._insert_zim_schedule(
            schedule_id=b"schedule_456",
            builder_id=builder_id.encode("utf-8"),
            rq_job_id=b"task-id-non-zim",
            last_updated_at="20221225000102",
            remaining_generations=None,
        )
        self.wp10db.commit()

        self.app = create_app()
        with self.override_db(self.app), self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.post(
                "/v1/builders/zim/status?token=hook-token-abc",
                json={
                    "id": "task-id-non-zim",
                    "status": "succeeded",
                    "files": {"zimcheck-report.txt": {"status": "uploaded"}},
                },
            )
            self.assertEqual("204 NO CONTENT", rv.status)

        with self.wp10db.cursor() as cursor:
            cursor.execute(
                "SELECT z_status FROM zim_tasks WHERE z_task_id = 'task-id-non-zim'"
            )
            status = cursor.fetchone()

        self.assertIsNotNone(status)
        self.assertEqual(b"REQUESTED", status["z_status"])

    def test_zimfarm_status(self):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)
        self._insert_zim_schedule(
            schedule_id=b"schedule_123",
            builder_id=builder_id.encode("utf-8"),
            rq_job_id=b"task-id-1234",
            last_updated_at="20240101000000",
        )
        with self.app.test_client() as client:
            rv = client.get("/v1/builders/%s/zim/status" % builder_id)
        self.assertEqual("200 OK", rv.status)
        self.assertEqual(
            {
                "error_url": "https://fake.farm/v2/tasks/task-id-1234",
                "status": "FILE_READY",
                "title": None,
                "description": None,
                "long_description": None,
                "is_deleted": None,
                "active_schedule": ANY,
            },
            rv.get_json(),
        )

    @patch(
        "wp1.logic.builder.zimfarm.zim_file_url_for_task_id",
        return_value="http://fake-file-host.fake/1234/file.zim",
    )
    def test_latest_zim_file_for_builder(self, mock_zimfarm):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)
        self.app = create_app()
        with self.app.test_client() as client:
            rv = client.get("/v1/builders/%s/zim/latest" % builder_id)
        self.assertEqual("302 FOUND", rv.status)
        self.assertEqual(
            "http://fake-file-host.fake/1234/file.zim", rv.headers["Location"]
        )

    def test_latest_zim_file_for_builder_404(self):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)
        self.app = create_app()
        with self.app.test_client() as client:
            rv = client.get("/v1/builders/abcd-1234/zim/latest")
        self.assertEqual("404 NOT FOUND", rv.status)

    @patch(
        "wp1.logic.builder.zimfarm.zim_file_url_for_task_id",
        return_value="http://fake-file-host.fake/1234/file.zim",
    )
    @patch("wp1.logic.selection.utcnow")
    def test_latest_zim_file_for_builder_410_when_expired(
        self, mock_utcnow, mock_zimfarm
    ):
        """Expired ZIM files (older than 2 weeks) should return 410 Gone."""
        # Set z_updated_at to a timestamp that is 3 weeks in the past so that
        # is_zim_file_deleted() returns True.
        three_weeks_ago = datetime.datetime(2020, 12, 4, 10, 55, 44)
        mock_utcnow.return_value = datetime.datetime(2020, 12, 25, 10, 55, 44)

        builder_id = self._insert_builder()
        self._insert_selections(builder_id)

        # Update z_updated_at to a time older than the 2-week TTL.
        with self.wp10db.cursor() as cursor:
            cursor.execute(
                "UPDATE zim_tasks SET z_updated_at = %s WHERE z_id = 1",
                (three_weeks_ago.strftime("%Y%m%d%H%M%S"),),
            )
        self.wp10db.commit()

        self.app = create_app()
        with self.app.test_client() as client:
            rv = client.get("/v1/builders/%s/zim/latest" % builder_id)
        self.assertEqual("410 GONE", rv.status)
        data = rv.get_json()
        self.assertIn("error_messages", data)
        self.assertTrue(len(data["error_messages"]) > 0)

    def test_latest_selection_article_count_for_builder(self):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)
        self.app = create_app()
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user"] = self.USER
            rv = client.get(
                "/v1/builders/%s/selection/latest/article_count" % builder_id
            )
        self.assertEqual("200 OK", rv.status)
        self.assertEqual(
            {
                "selection": {
                    "id": "3",
                    "article_count": 1000,
                    "max_article_count": MAX_ZIMFARM_ARTICLE_COUNT,
                }
            },
            rv.get_json(),
        )

    def test_latest_selection_article_count_for_builder_wrong_user(self):
        builder_id = self._insert_builder()
        self._insert_selections(builder_id)
        self.app = create_app()
        with self.app.test_client() as client:
            rv = client.get(
                "/v1/builders/%s/selection/latest/article_count" % builder_id
            )
        self.assertEqual("401 UNAUTHORIZED", rv.status)
        self.assertEqual("401 UNAUTHORIZED", rv.status)
