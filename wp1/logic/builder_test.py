import datetime
from unittest.mock import ANY, MagicMock, call, patch

import attr

from wp1.base_db_test import BaseWpOneDbTest
from wp1.environment import Environment
from wp1.exceptions import (
    InvalidZimTitleError,
    ObjectNotFoundError,
    UserNotAuthorizedError,
    ZimFarmError,
)
from wp1.logic import builder as logic_builder
from wp1.models.wp10.builder import Builder
from wp1.models.wp10.zim_file import ZimTask
from wp1.models.wp10.zim_schedule import ZimSchedule
from wp1.selection.models.simple import Builder as SimpleBuilder


class BuilderTest(BaseWpOneDbTest):

    expected_builder = {
        "b_id": b"1a-2b-3c-4d",
        "b_name": b"My Builder",
        "b_user_id": b"1234",
        "b_project": b"en.wikipedia.fake",
        "b_model": b"wp1.selection.models.simple",
        "b_params": b'{"list": ["a", "b", "c"]}',
        "b_created_at": b"20191225044444",
        "b_updated_at": b"20191225044444",
        "b_current_version": 0,
        "b_selection_zim_version": 0,
    }

    expected_lists = [
        {
            "id": "1a-2b-3c-4d",
            "name": "My Builder",
            "project": "en.wikipedia.fake",
            "created_at": 1577249084,
            "updated_at": 1577249084,
            "model": "wp1.selection.models.simple",
            "s_id": "1",
            "s_updated_at": 1577249084,
            "s_content_type": "text/tab-separated-values",
            "s_extension": "tsv",
            "s_url": "http://test.server.fake/v1/builders/1a-2b-3c-4d/selection/latest.tsv",
            "s_status": "OK",
            "z_updated_at": None,
            "z_url": None,
            "z_status": "NOT_REQUESTED",
            "z_is_deleted": None,
            "active_schedule": None,
        }
    ]

    expected_lists_with_multiple_selections = [
        {
            "id": "1a-2b-3c-4d",
            "name": "My Builder",
            "project": "en.wikipedia.fake",
            "created_at": 1577249084,
            "updated_at": 1577249084,
            "model": "wp1.selection.models.simple",
            "s_id": "2",
            "s_updated_at": 1577249084,
            "s_content_type": "application/vnd.ms-excel",
            "s_extension": "xls",
            "s_url": "http://test.server.fake/v1/builders/1a-2b-3c-4d/selection/latest.xls",
            "s_status": "OK",
            "z_updated_at": None,
            "z_url": None,
            "z_status": "NOT_REQUESTED",
            "z_is_deleted": None,
            "active_schedule": None,
        },
        {
            "id": "1a-2b-3c-4d",
            "name": "My Builder",
            "project": "en.wikipedia.fake",
            "created_at": 1577249084,
            "updated_at": 1577249084,
            "model": "wp1.selection.models.simple",
            "s_id": "1",
            "s_updated_at": 1577249084,
            "s_content_type": "text/tab-separated-values",
            "s_extension": "tsv",
            "s_url": "http://test.server.fake/v1/builders/1a-2b-3c-4d/selection/latest.tsv",
            "s_status": "OK",
            "z_updated_at": None,
            "z_url": None,
            "z_status": "NOT_REQUESTED",
            "z_is_deleted": None,
            "active_schedule": None,
        },
    ]

    expected_lists_with_no_selections = [
        {
            "id": "1a-2b-3c-4d",
            "name": "My Builder",
            "project": "en.wikipedia.fake",
            "created_at": 1577249084,
            "updated_at": 1577249084,
            "model": "wp1.selection.models.simple",
            "s_id": None,
            "s_updated_at": None,
            "s_content_type": None,
            "s_extension": None,
            "s_url": None,
            "s_status": None,
            "z_updated_at": None,
            "z_url": None,
            "z_status": None,
            "z_is_deleted": None,
            "active_schedule": None,
        }
    ]

    expected_lists_with_unmapped_selections = [
        {
            "id": "1a-2b-3c-4d",
            "name": "My Builder",
            "project": "en.wikipedia.fake",
            "created_at": 1577249084,
            "updated_at": 1577249084,
            "model": "wp1.selection.models.simple",
            "s_id": "1",
            "s_updated_at": 1577249084,
            "s_content_type": "foo/bar-baz",
            "s_extension": "???",
            "s_url": None,
            "s_status": "OK",
            "z_updated_at": None,
            "z_url": None,
            "z_status": "NOT_REQUESTED",
            "z_is_deleted": None,
            "active_schedule": None,
        }
    ]

    expected_list_with_zimfarm_status = [
        {
            "id": "1a-2b-3c-4d",
            "name": "My Builder",
            "project": "en.wikipedia.fake",
            "created_at": 1577249084,
            "updated_at": 1577249084,
            "model": "wp1.selection.models.simple",
            "s_id": "1",
            "s_updated_at": 1577249084,
            "s_content_type": "text/tab-separated-values",
            "s_extension": "tsv",
            "s_url": "http://test.server.fake/v1/builders/1a-2b-3c-4d/selection/latest.tsv",
            "s_status": "OK",
            "z_updated_at": 1671927082,
            "z_url": "http://test.server.fake/v1/builders/1a-2b-3c-4d/zim/latest",
            "z_status": "FILE_READY",
            "z_is_deleted": True,
            "active_schedule": None,
        }
    ]

    def _insert_builder(self, current_version=None, zim_version=None):
        if current_version is None:
            current_version = 1
        value_dict = attr.asdict(self.builder)
        value_dict["b_current_version"] = current_version
        value_dict["b_id"] = b"1a-2b-3c-4d"
        if zim_version is not None:
            value_dict["b_selection_zim_version"] = zim_version
        with self.wp10db.cursor() as cursor:
            cursor.execute(
                """INSERT INTO builders
               (b_id, b_name, b_user_id, b_project, b_params, b_model, b_created_at,
                b_updated_at, b_current_version, b_selection_zim_version)
             VALUES
               (%(b_id)s, %(b_name)s, %(b_user_id)s, %(b_project)s, %(b_params)s,
                %(b_model)s, %(b_created_at)s, %(b_updated_at)s, %(b_current_version)s,
                %(b_selection_zim_version)s)
          """,
                value_dict,
            )
        self.wp10db.commit()
        return value_dict["b_id"]

    def _insert_zim_schedule(
        self,
        schedule_id=b"schedule_123",
        builder_id=None,
        rq_job_id=b"rq_job_id_123",
        last_updated_at=b"20191225044444",
        title=None,
        description=None,
        long_description=None,
        remaining_generations=3,
    ):
        if builder_id is None:
            builder_id = b"1a-2b-3c-4d"
        with self.wp10db.cursor() as cursor:
            cursor.execute(
                """INSERT INTO zim_schedules (s_id, s_builder_id, s_rq_job_id, s_remaining_generations, s_last_updated_at, s_title, s_description, s_long_description)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
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
                ),
            )
        self.wp10db.commit()
        return schedule_id

    def _insert_selection(
        self,
        id_,
        content_type,
        version=1,
        object_key="selections/foo/1234/name.tsv",
        builder_id=b"1a-2b-3c-4d",
        has_errors=False,
        zim_file_ready=False,
        zim_task_id="5678",
        skip_zim=False,
        zim_schedule_id=b"schedule_123",
    ):
        if has_errors:
            status = "CAN_RETRY"
            error_messages = '{"error_messages":["There was an error"]}'
        else:
            status = "OK"
            error_messages = None

        zimfarm_status = b"NOT_REQUESTED"
        zim_file_updated_at = None
        if zim_file_ready:
            zimfarm_status = b"FILE_READY"
            zim_file_updated_at = b"20221225001122"

        with self.wp10db.cursor() as cursor:
            cursor.execute(
                """INSERT INTO selections
               (s_id, s_builder_id, s_content_type, s_updated_at, s_version,
                s_object_key, s_status, s_error_messages)
             VALUES
               (%s, %s, %s, "20191225044444", %s, %s, %s, %s)
          """,
                (
                    id_,
                    builder_id,
                    content_type,
                    version,
                    object_key,
                    status,
                    error_messages,
                ),
            )
            if not skip_zim:
                cursor.execute(
                    """INSERT INTO zim_tasks
                 (z_selection_id, z_zim_schedule_id, z_task_id, z_status, z_updated_at,
                  z_requested_at)
               VALUES
                 (%s, %s, %s, %s, %s, "20230101020202")
            """,
                    (
                        id_,
                        zim_schedule_id,
                        zim_task_id,
                        zimfarm_status,
                        zim_file_updated_at,
                    ),
                )
        self.wp10db.commit()

    def _setup_failed_zim_regeneration_scenario(
        self,
        zim_schedule_id=b"schedule-123",
        old_task_id="old-task-id",
        create_new_selection=False,
    ):
        self._insert_zim_schedule(zim_schedule_id, self.builder.b_id)

        with self.wp10db.cursor() as cursor:
            # Insert selection v1 with failed ZIM
            cursor.execute(
                """INSERT INTO selections
                (s_id, s_builder_id, s_updated_at, s_content_type, s_version,
                 s_object_key, s_article_count)
                VALUES (%s, %s, '20250102000000', 'text/tab-separated-values', 1,
                        'old.tsv', 100)""",
                (1, self.builder.b_id),
            )
            cursor.execute(
                """INSERT INTO zim_tasks
                (z_selection_id, z_zim_schedule_id, z_status, z_task_id)
                VALUES (%s, %s, 'FAILED', %s)""",
                (1, zim_schedule_id, old_task_id),
            )
            # Optionally create selection v2
            if create_new_selection:
                cursor.execute(
                    """INSERT INTO selections
                    (s_id, s_builder_id, s_updated_at, s_content_type, s_version,
                     s_object_key, s_article_count)
                    VALUES (%s, %s, '20250103000000', 'text/tab-separated-values', 2,
                            'new.tsv', 100)""",
                    (2, self.builder.b_id),
                )
                cursor.execute(
                    "UPDATE builders SET b_current_version = 2 WHERE b_id = %s",
                    (self.builder.b_id,),
                )

        self.wp10db.commit()
        return zim_schedule_id

    def _get_builder_by_user_id(self):
        with self.wp10db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM builders WHERE b_user_id=%(b_user_id)s",
                {"b_user_id": b"1234"},
            )
            db_lists = cursor.fetchone()
            return db_lists

    def setUp(self):
        super().setUp()
        self.builder = Builder(
            b_id=b"1a-2b-3c-4d",
            b_name=b"My Builder",
            b_user_id=b"1234",
            b_project=b"en.wikipedia.fake",
            b_model=b"wp1.selection.models.simple",
            b_params=b'{"list": ["a", "b", "c"]}',
            b_created_at=b"20191225044444",
            b_updated_at=b"20191225044444",
            b_current_version=1,
            b_selection_zim_version=1,
        )

    @patch(
        "wp1.models.wp10.builder.utcnow",
        return_value=datetime.datetime(2019, 12, 25, 4, 44, 44),
    )
    @patch("wp1.models.wp10.builder.builder_id", return_value=b"1a-2b-3c-4d")
    def test_create_or_update_builder_create(self, mock_builder_id, mock_utcnow):
        logic_builder.create_or_update_builder(
            self.wp10db,
            "My Builder",
            "1234",
            "en.wikipedia.fake",
            {"list": ["a", "b", "c"]},
            "wp1.selection.models.simple",
        )
        actual = self._get_builder_by_user_id()
        self.assertEqual(self.expected_builder, actual)

    @patch(
        "wp1.models.wp10.builder.utcnow",
        return_value=datetime.datetime(2020, 1, 1, 5, 55, 55),
    )
    def test_create_or_update_builder_update(self, mock_utcnow):
        id_ = self._insert_builder()
        actual = logic_builder.create_or_update_builder(
            self.wp10db,
            "Builder 2",
            "1234",
            "zz.wikipedia.fake",
            {"list": ["a", "b", "c", "d"]},
            "wp1.selection.models.simple",
            builder_id=id_,
        )
        self.assertTrue(actual)
        expected = dict(**self.expected_builder)
        expected["b_name"] = b"Builder 2"
        expected["b_project"] = b"zz.wikipedia.fake"
        expected["b_params"] = b'{"list": ["a", "b", "c", "d"]}'
        expected["b_updated_at"] = b"20200101055555"
        expected["b_current_version"] = 1
        expected["b_selection_zim_version"] = 1
        actual = self._get_builder_by_user_id()
        self.assertEqual(expected, actual)

    @patch(
        "wp1.models.wp10.builder.utcnow",
        return_value=datetime.datetime(2019, 12, 25, 4, 44, 44),
    )
    @patch("wp1.models.wp10.builder.builder_id", return_value=b"1a-2b-3c-4d")
    def test_insert_builder(self, mock_builder_id, mock_utcnow):
        logic_builder.insert_builder(self.wp10db, self.builder)
        actual = self._get_builder_by_user_id()
        self.assertEqual(self.expected_builder, actual)

    @patch(
        "wp1.models.wp10.builder.utcnow",
        return_value=datetime.datetime(2019, 12, 25, 4, 44, 44),
    )
    @patch("wp1.models.wp10.builder.builder_id", return_value=b"1a-2b-3c-4d")
    def test_insert_builder_returns_id(self, mock_builder_id, mock_utcnow):
        actual = logic_builder.insert_builder(self.wp10db, self.builder)
        self.assertEqual(b"1a-2b-3c-4d", actual)

    def test_get_builder(self):
        id_ = self._insert_builder()
        actual = logic_builder.get_builder(self.wp10db, id_)
        self.builder.b_id = id_
        self.assertEqual(self.builder, actual)

    def test_materialize_builder_with_connections(self):
        s3 = MagicMock()
        redis = MagicMock()

        TestBuilderClass = MagicMock()
        materialize_mock = MagicMock()
        TestBuilderClass.return_value = materialize_mock

        self._insert_builder()
        self._insert_selection(1, "text/tab-separated-values")

        logic_builder.materialize_builder(
            TestBuilderClass,
            self.builder,
            "text/tab-separated-values",
            s3,
            redis,
            self.wp10db,
        )
        materialize_mock.materialize.assert_called_once_with(
            ANY, ANY, self.builder, "text/tab-separated-values", 2
        )

        actual = self._get_builder_by_user_id()
        expected = dict(**self.expected_builder)
        expected["b_current_version"] = 2
        expected["b_selection_zim_version"] = 2
        self.assertEqual(expected, actual)

    @patch("wp1.logic.builder.wp10_connect")
    @patch("wp1.logic.builder.connect_storage")
    def test_materialize_builder(self, mock_connect_storage, mock_connect_wp10):
        mock_connect_wp10.return_value = self.wp10db
        TestBuilderClass = MagicMock()
        materialize_mock = MagicMock()
        TestBuilderClass.return_value = materialize_mock

        orig_close = self.wp10db.close
        try:
            self.wp10db.close = lambda: True
            self._insert_builder()
            self._insert_selection(1, "text/tab-separated-values")

            logic_builder.materialize_builder(
                TestBuilderClass, self.builder, "text/tab-separated-values"
            )
            materialize_mock.materialize.assert_called_once_with(
                ANY, ANY, self.builder, "text/tab-separated-values", 2
            )
        finally:
            self.wp10db.close = orig_close

        actual = self._get_builder_by_user_id()
        expected = dict(**self.expected_builder)
        expected["b_current_version"] = 2
        expected["b_selection_zim_version"] = 2
        self.assertEqual(expected, actual)

    @patch("wp1.logic.builder.wp10_connect")
    @patch("wp1.logic.builder.redis_connect")
    @patch("wp1.logic.builder.connect_storage")
    @patch("wp1.logic.builder.handle_zim_generation")
    def test_materialize_builder_no_update_zim_version(
        self,
        mock_handle_zim_generation,
        mock_connect_storage,
        mock_redis_connect,
        mock_connect_wp10,
    ):
        s3 = MagicMock()
        redis = MagicMock()
        mock_connect_wp10.return_value = self.wp10db
        mock_connect_storage.return_value = s3
        mock_redis_connect.return_value = redis
        TestBuilderClass = MagicMock()
        materialize_mock = MagicMock()
        TestBuilderClass.return_value = materialize_mock

        orig_close = self.wp10db.close
        try:
            self.wp10db.close = lambda: True
            self._insert_builder()
            self._insert_selection(1, "text/tab-separated-values", zim_file_ready=True)
            self._insert_zim_schedule(b"schedule_123", b"1a-2b-3c-4d", b"rq_job_id_123")

            logic_builder.materialize_builder(
                TestBuilderClass, self.builder, "text/tab-separated-values"
            )
            mock_handle_zim_generation.assert_called_once_with(
                redis,
                self.wp10db,
                self.builder.b_id,
                title=None,
                description=None,
                long_description=None,
            )
        finally:
            self.wp10db.close = orig_close

        builder = self._get_builder_by_user_id()
        expected = dict(**self.expected_builder)
        expected["b_current_version"] = 2
        expected["b_selection_zim_version"] = 1
        self.assertEqual(expected, builder)

    @patch(
        "wp1.models.wp10.builder.utcnow",
        return_value=datetime.datetime(2019, 12, 25, 4, 44, 44),
    )
    def test_get_builders(self, mock_utcnow):
        self._insert_selection(1, "text/tab-separated-values")
        self._insert_builder()
        article_data = logic_builder.get_builders_with_selections(self.wp10db, 1234)
        self.assertEqual(self.expected_lists, article_data)

    @patch(
        "wp1.models.wp10.builder.utcnow",
        return_value=datetime.datetime(2019, 12, 25, 4, 44, 44),
    )
    def test_get_builders_with_multiple_selections(self, mock_utcnow):
        self._insert_selection(
            1, "text/tab-separated-values", object_key="object_key_1"
        )
        self._insert_selection(2, "application/vnd.ms-excel", object_key="object_key_2")
        self._insert_builder()
        article_data = logic_builder.get_builders_with_selections(self.wp10db, 1234)
        self.assertObjectListsEqual(
            self.expected_lists_with_multiple_selections, article_data
        )

    @patch(
        "wp1.models.wp10.builder.utcnow",
        return_value=datetime.datetime(2019, 12, 25, 4, 44, 44),
    )
    def test_get_builders_with_no_selections(self, mock_utcnow):
        self._insert_builder()
        article_data = logic_builder.get_builders_with_selections(self.wp10db, 1234)
        self.assertEqual(self.expected_lists_with_no_selections, article_data)

    @patch(
        "wp1.models.wp10.builder.utcnow",
        return_value=datetime.datetime(2019, 12, 25, 4, 44, 44),
    )
    def test_get_builders_with_selections_no_zim_tasks(self, mock_utcnow):
        id_ = self._insert_builder()
        self._insert_selection(1, "text/tab-separated-values", skip_zim=True)
        article_data = logic_builder.get_builders_with_selections(self.wp10db, 1234)
        self.assertEqual(self.expected_lists, article_data)

    @patch(
        "wp1.models.wp10.builder.utcnow",
        return_value=datetime.datetime(2019, 12, 25, 4, 44, 44),
    )
    def test_get_builders_empty_lists(self, mock_utcnow):
        self._insert_selection(1, "text/tab-separated-values")
        id_ = self._insert_builder()
        article_data = logic_builder.get_builders_with_selections(self.wp10db, "0000")
        self.assertEqual([], article_data)

    @patch(
        "wp1.models.wp10.builder.utcnow",
        return_value=datetime.datetime(2019, 12, 25, 4, 44, 44),
    )
    def teest_get_builders_ignores_old_versions(self, mock_utcnow):
        self._insert_selection(1, "text/tab-separated-values", 1)
        self._insert_selection(2, "application/vnd.ms-excel", 1)
        self._insert_selection(3, "text/tab-separated-values", 2)
        self._insert_selection(4, "application/vnd.ms-excel", 2)
        id_ = self._insert_builder()
        article_data = logic_builder.get_builders_with_selections(self.wp10db, id_)
        self.assertObjectListsEqual(
            self.expected_lists_with_multiple_selections, article_data
        )

    @patch(
        "wp1.models.wp10.builder.utcnow",
        return_value=datetime.datetime(2019, 12, 25, 4, 44, 44),
    )
    def test_get_builders_with_selection_no_builders(self, mock_utcnow):
        self._insert_selection(1, "text/tab-separated-values")
        article_data = logic_builder.get_builders_with_selections(self.wp10db, "0000")
        self.assertEqual([], article_data)

    @patch(
        "wp1.models.wp10.builder.utcnow",
        return_value=datetime.datetime(2019, 12, 25, 4, 44, 44),
    )
    def test_get_builders_with_unmapped_content_type(self, mock_utcnow):
        self._insert_selection(
            1,
            "foo/bar-baz",
            object_key="selections/wp1.selection.models.simple/1/My Builder.???",
        )
        self._insert_builder()
        article_data = logic_builder.get_builders_with_selections(self.wp10db, "1234")
        self.assertObjectListsEqual(
            self.expected_lists_with_unmapped_selections, article_data
        )

    @patch(
        "wp1.models.wp10.builder.utcnow",
        return_value=datetime.datetime(2020, 12, 25, 4, 44, 44),
    )
    def test_get_builders_deleted_zim(self, mock_utcnow):
        self._insert_selection(
            1, "text/tab-separated-values", zim_file_ready=True, version=1
        )
        self._insert_selection(
            2, "text/tab-separated-values", zim_file_ready=False, version=2
        )
        self._insert_builder()
        article_data = logic_builder.get_builders_with_selections(self.wp10db, "1234")
        self.assertObjectListsEqual(
            self.expected_list_with_zimfarm_status, article_data
        )

    @patch(
        "wp1.models.wp10.builder.utcnow",
        return_value=datetime.datetime(2019, 12, 25, 4, 44, 44),
    )
    def test_get_builders_zimfarm_status(self, mock_utcnow):
        self._insert_selection(
            1, "text/tab-separated-values", zim_file_ready=True, version=1
        )
        self._insert_selection(
            2, "text/tab-separated-values", zim_file_ready=False, version=2
        )
        self._insert_builder()
        article_data = logic_builder.get_builders_with_selections(self.wp10db, "1234")
        self.assertObjectListsEqual(
            self.expected_list_with_zimfarm_status, article_data
        )

    def test_update_builder_doesnt_exist(self):
        actual = logic_builder.update_builder(self.wp10db, self.builder)
        self.assertFalse(actual)

    def test_update_builder_user_id_doesnt_match(self):
        self._insert_builder()
        builder = Builder(
            b_id=b"1a-2b-3c-4d",
            b_name=b"My Builder",
            b_user_id=b"5555",  # Different user_id
            b_project=b"en.wikipedia.fake",
            b_model=b"wp1.selection.models.simple",
            b_params=b'{"list": ["a", "b", "c"]}',
        )
        actual = logic_builder.update_builder(self.wp10db, builder)
        self.assertFalse(actual)

    def test_update_builder_wrong_id(self):
        self._insert_builder()
        builder = Builder(
            b_id=b"100",  # Wrong ID
            b_name=b"My Builder",
            b_user_id=b"1234",
            b_project=b"en.wikipedia.fake",
            b_model=b"wp1.selection.models.simple",
            b_params=b'{"list": ["a", "b", "c"]}',
        )
        actual = logic_builder.update_builder(self.wp10db, builder)
        self.assertFalse(actual)

    def test_update_builder_success(self):
        self._insert_builder()
        builder = Builder(
            b_id=b"1a-2b-3c-4d",
            b_name=b"My Builder",
            b_user_id=b"1234",
            b_project=b"en.wikipedia.fake",
            b_model=b"wp1.selection.models.simple",
            b_params=b'{"list": ["a", "b", "c"]}',
        )
        actual = logic_builder.update_builder(self.wp10db, builder)
        self.assertTrue(actual)

    def test_update_builder_updates_fields(self):
        self._insert_builder()
        builder = Builder(
            b_id=b"1a-2b-3c-4d",
            b_name=b"Builder 2",
            b_user_id=b"1234",
            b_project=b"zz.wikipedia.fake",
            b_model=b"wp1.selection.models.complex",
            b_params=b'{"list": ["1", "b", "c"]}',
            b_created_at=b"20191225044444",
            b_updated_at=b"20211111044444",
            b_current_version=1,
            b_selection_zim_version=1,
        )
        actual = logic_builder.update_builder(self.wp10db, builder)
        self.assertTrue(actual)

        with self.wp10db.cursor() as cursor:
            cursor.execute("SELECT * FROM builders where b_id = %s", ("1a-2b-3c-4d",))
            db_builder = cursor.fetchone()
            actual_builder = Builder(**db_builder)
        self.assertEqual(builder, actual_builder)

    def test_latest_url_for(self):
        actual = logic_builder.latest_url_for(15, "text/tab-separated-values")
        self.assertEqual(
            actual, "http://test.server.fake/v1/builders/15/selection/latest.tsv"
        )
        actual = logic_builder.latest_url_for(439, "application/vnd.ms-excel")
        self.assertEqual(
            actual, "http://test.server.fake/v1/builders/439/selection/latest.xls"
        )

    def test_latest_url_for_unmapped_content_type(self):
        actual = logic_builder.latest_url_for(150, "foo/bar-baz")
        self.assertIsNone(actual)

    @patch("wp1.logic.builder.CREDENTIALS", {})
    def test_latest_url_for_no_server_url(self):
        actual = logic_builder.latest_url_for(15, "text/tab-separated-values")
        self.assertIsNone(actual)

    def test_latest_selection_url(self):
        builder_id = self._insert_builder()
        self._insert_selection(1, "text/tab-separated-values")

        actual = logic_builder.latest_selection_url(self.wp10db, builder_id, "tsv")

        self.assertEqual(
            actual, "http://credentials.not.found.fake/selections/foo/1234/name.tsv"
        )

    def test_latest_selection_url_unknown_extension(self):
        builder_id = self._insert_builder()
        self._insert_selection(1, "text/tab-separated-values")

        actual = logic_builder.latest_selection_url(self.wp10db, builder_id, "foo")

        self.assertIsNone(actual)

    def test_latest_selection_url_missing_builder(self):
        builder_id = self._insert_builder()
        self._insert_selection(1, "text/tab-separated-values")

        actual = logic_builder.latest_selection_url(self.wp10db, "foo-bar-baz", "tsv")

        self.assertIsNone(actual)

    def test_latest_selection_url_missing_selection(self):
        builder_id = self._insert_builder()

        actual = logic_builder.latest_selection_url(self.wp10db, builder_id, "tsv")

        self.assertIsNone(actual)

    def test_latest_selection_url_no_object_key(self):
        builder_id = self._insert_builder()
        self._insert_selection(1, "text/tab-separated-values", object_key=None)

        actual = logic_builder.latest_selection_url(self.wp10db, builder_id, "tsv")

        self.assertIsNone(actual)

    def test_latest_selection_url_unrelated_selections(self):
        builder_id = self._insert_builder()
        self._insert_selection(1, "text/tab-separated-values", builder_id=-1)
        self._insert_selection(2, "text/tab-separated-values", builder_id=-2)
        self._insert_selection(3, "text/tab-separated-values", builder_id=-3)

        actual = logic_builder.latest_selection_url(self.wp10db, builder_id, "tsv")

        self.assertIsNone(actual)

    def _insert_builder_with_multiple_version_selections(self):
        builder_id = self._insert_builder(current_version=3, zim_version=2)
        self._insert_selection(
            1,
            "text/tab-separated-values",
            version=1,
            object_key="object_key_1",
            builder_id=builder_id,
        )
        self._insert_selection(
            2,
            "application/vnd.ms-excel",
            version=1,
            object_key="object_key_2",
            builder_id=builder_id,
        )
        self._insert_selection(
            3,
            "text/tab-separated-values",
            version=2,
            object_key="object_key_3",
            builder_id=builder_id,
        )
        self._insert_selection(
            4,
            "text/tab-separated-values",
            version=3,
            object_key="proper/selection/4321/name.tsv",
            builder_id=builder_id,
        )

        return builder_id

    def test_latest_selection_url_multiple_versions(self):
        builder_id = self._insert_builder_with_multiple_version_selections()

        actual = logic_builder.latest_selection_url(self.wp10db, builder_id, "tsv")

        self.assertEqual(
            actual, "http://credentials.not.found.fake/proper/selection/4321/name.tsv"
        )

    @patch(
        "wp1.logic.builder.zimfarm.zim_file_url_for_task_id",
        return_value="https://zim.fake/1234",
    )
    def test_latest_zim_file_url_for(self, mock_zimfarm_url_for):
        builder_id = self._insert_builder_with_multiple_version_selections()
        with self.wp10db.cursor() as cursor:
            cursor.execute(
                '''UPDATE zim_tasks z
                          INNER JOIN selections s ON s.s_id = z.z_selection_id
                          INNER JOIN builders b ON b.b_selection_zim_version = s.s_version
                        SET z_status = "FILE_READY"'''
            )

        actual = logic_builder.latest_zim_file_url_for(self.wp10db, builder_id)

        self.assertEqual("https://zim.fake/1234", actual)

    @patch(
        "wp1.logic.builder.zimfarm.zim_file_url_for_task_id",
        return_value="https://zim.fake/1234",
    )
    def test_latest_zim_file_url_for_not_ready(self, mock_zimfarm_url_for):
        builder_id = self._insert_builder_with_multiple_version_selections()

        actual = logic_builder.latest_zim_file_url_for(self.wp10db, builder_id)

        self.assertIsNone(actual)

    @patch("wp1.logic.builder.queues.cancel_scheduled_job")
    @patch("wp1.logic.builder.zimfarm.delete_zimfarm_schedule_by_builder_id")
    @patch("wp1.logic.builder.logic_selection")
    def test_delete_builder(
        self, mock_selection, mock_delete_schedule, mock_cancel_job
    ):
        builder_id = self._insert_builder_with_multiple_version_selections()

        actual = logic_builder.delete_builder(self.wp10db, 1234, builder_id)

        self.assertTrue(actual["db_delete_success"])

    @patch("wp1.logic.builder.queues.cancel_scheduled_job")
    @patch("wp1.logic.builder.zimfarm.delete_zimfarm_schedule_by_builder_id")
    @patch("wp1.logic.builder.logic_selection")
    def test_delete_builder_user_id_unmatched(
        self, mock_selection, mock_delete_schedule, mock_cancel_job
    ):
        builder_id = self._insert_builder_with_multiple_version_selections()

        with self.assertRaises(UserNotAuthorizedError):
            logic_builder.delete_builder(self.wp10db, 4321, builder_id)

    @patch("wp1.logic.builder.queues.cancel_scheduled_job")
    @patch("wp1.logic.builder.zimfarm.delete_zimfarm_schedule_by_builder_id")
    @patch("wp1.logic.builder.logic_selection")
    def test_delete_builder_user_builder_id_unmatched(
        self, mock_selection, mock_delete_schedule, mock_cancel_job
    ):
        self._insert_builder_with_multiple_version_selections()

        with self.assertRaises(ObjectNotFoundError):
            logic_builder.delete_builder(self.wp10db, 1234, "abcd")

    @patch("wp1.logic.builder.queues.cancel_scheduled_job")
    @patch("wp1.logic.builder.zimfarm.delete_zimfarm_schedule_by_builder_id")
    @patch("wp1.logic.builder.logic_selection")
    def test_delete_builder_user_no_selections(
        self, mock_selection, mock_delete_schedule, mock_cancel_job
    ):
        builder_id = self._insert_builder()

        actual = logic_builder.delete_builder(self.wp10db, 1234, builder_id)

        self.assertTrue(actual["db_delete_success"])

    @patch("wp1.logic.builder.zimfarm.delete_zimfarm_schedule_by_builder_id")
    @patch("wp1.queues.cancel_scheduled_job")
    @patch("wp1.logic.builder.logic_selection")
    def test_delete_builder_deletes_zimfarm_schedule(
        self, mock_selection, mock_cancel_job, mock_delete_zimfarm
    ):
        builder_id = self._insert_builder()
        self._insert_zim_schedule(builder_id=builder_id)
        mock_delete_zimfarm.return_value = None

        actual = logic_builder.delete_builder(self.wp10db, 1234, builder_id)

        self.assertTrue(actual["db_delete_success"])
        self.assertTrue(actual["zimfarm_delete_success"])
        mock_delete_zimfarm.assert_called_once()
        mock_cancel_job.assert_called_once()

        # Check that the schedule is deleted from the DB
        with self.wp10db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM zim_schedules WHERE s_builder_id = %s", (builder_id,)
            )
            schedule = cursor.fetchone()
        self.assertIsNone(schedule)

    @patch("wp1.logic.builder.zimfarm.delete_zimfarm_schedule_by_builder_id")
    @patch("wp1.logic.builder.logic_selection")
    def test_delete_builder_zimfarm_delete_fails(
        self, mock_selection, mock_delete_zimfarm
    ):
        builder_id = self._insert_builder()
        mock_delete_zimfarm.side_effect = Exception("Zimfarm error")

        actual = logic_builder.delete_builder(self.wp10db, 1234, builder_id)

        self.assertTrue(actual["db_delete_success"])
        self.assertFalse(actual["zimfarm_delete_success"])
        mock_delete_zimfarm.assert_called_once()

    @patch("wp1.logic.builder.queues.cancel_scheduled_job")
    @patch("wp1.logic.builder.zimfarm.delete_zimfarm_schedule_by_builder_id")
    @patch("wp1.logic.builder.logic_selection.delete_keys_from_storage")
    def test_delete_builder_deletes_object_keys(
        self, mock_delete_keys, mock_delete_schedule, mock_cancel_job
    ):
        builder_id = self._insert_builder_with_multiple_version_selections()
        mock_delete_keys.return_value = True

        actual = logic_builder.delete_builder(self.wp10db, 1234, builder_id)

        self.assertTrue(actual["db_delete_success"])
        self.assertTrue(actual["s3_delete_success"])
        mock_delete_keys.assert_called_once_with(
            [
                b"object_key_1",
                b"object_key_2",
                b"object_key_3",
                b"proper/selection/4321/name.tsv",
            ]
        )

    @patch("wp1.logic.builder.queues.cancel_scheduled_job")
    @patch("wp1.logic.builder.zimfarm.delete_zimfarm_schedule_by_builder_id")
    @patch("wp1.logic.builder.logic_selection.delete_keys_from_storage")
    def test_delete_builder_object_keys_missing(
        self, mock_delete_keys, mock_delete_schedule, mock_cancel_job
    ):
        builder_id = self._insert_builder_with_multiple_version_selections()
        mock_delete_keys.return_value = True

        self._insert_selection(
            5,
            "application/vnd.ms-excel",
            version=3,
            object_key=None,
            builder_id=builder_id,
        )

        actual = logic_builder.delete_builder(self.wp10db, 1234, builder_id)

        self.assertTrue(actual["db_delete_success"])
        self.assertTrue(actual["s3_delete_success"])
        mock_delete_keys.assert_called_once_with(
            [
                b"object_key_1",
                b"object_key_2",
                b"object_key_3",
                b"proper/selection/4321/name.tsv",
            ]
        )

    @patch("wp1.logic.builder.queues.cancel_scheduled_job")
    @patch("wp1.logic.builder.zimfarm.delete_zimfarm_schedule_by_builder_id")
    @patch("wp1.logic.builder.logic_selection.delete_keys_from_storage")
    def test_delete_builder_cancels_scheduled_jobs(
        self, mock_delete_keys, mock_delete_schedule, mock_cancel_job
    ):
        builder_id = self._insert_builder()
        mock_delete_keys.return_value = True
        mock_cancel_job.return_value = True

        # Insert a zim schedule with an RQ job ID
        with self.wp10db.cursor() as cursor:
            cursor.execute(
                """INSERT INTO zim_schedules (s_id, s_builder_id, s_rq_job_id, s_last_updated_at)
             VALUES (%s, %s, %s, %s)
          """,
                (b"schedule_123", builder_id, b"rq_job_456", b"20191225044444"),
            )
        self.wp10db.commit()

        actual = logic_builder.delete_builder(self.wp10db, 1234, builder_id)

        self.assertTrue(actual["db_delete_success"])
        self.assertTrue(actual["rq_cancel_success"])
        mock_cancel_job.assert_called_once_with(ANY, b"rq_job_456")
        mock_delete_schedule.assert_called_once_with(ANY, builder_id)

    def test_latest_selections_with_errors(self):
        builder_id = self._insert_builder(current_version=2)
        self._insert_selection(
            1,
            "text/tab-separated-values",
            version=1,
            builder_id=builder_id,
            has_errors=True,
        )
        self._insert_selection(
            2,
            "text/tab-separated-values",
            version=2,
            builder_id=builder_id,
            has_errors=False,
        )
        self._insert_selection(
            3,
            "application/vnd.ms-excel",
            version=2,
            builder_id=builder_id,
            has_errors=True,
        )

        actual = logic_builder.latest_selections_with_errors(self.wp10db, builder_id)

        self.assertEqual(
            [
                {
                    "status": "CAN_RETRY",
                    "ext": "xls",
                    "error_messages": ["There was an error"],
                }
            ],
            actual,
        )

    def test_latest_selection_with_errors_no_errors(self):
        builder_id = self._insert_builder()
        self._insert_selection(
            1, "text/tab-separated-values", builder_id=builder_id, has_errors=False
        )
        self._insert_selection(
            2, "application/vnd.ms-excel", builder_id=builder_id, has_errors=False
        )

        actual = logic_builder.latest_selections_with_errors(self.wp10db, builder_id)

        self.assertEqual(0, len(actual))

    @patch("wp1.logic.builder.zimfarm.create_or_update_zimfarm_schedule")
    @patch("wp1.logic.builder.zimfarm.request_zimfarm_task")
    @patch(
        "wp1.logic.builder.utcnow",
        return_value=datetime.datetime(2022, 12, 25, 0, 1, 2),
    )
    def test_handle_zim_generation(
        self, mock_utcnow, mock_request_zimfarm_task, mock_create_zimfarm_schedule
    ):
        redis = MagicMock()
        mock_request_zimfarm_task.return_value = "1234-a"
        mock_create_zimfarm_schedule.return_value = ZimSchedule(
            s_id=b"schedule_123",
            s_builder_id=b"1a-2b-3c-4d",
            s_rq_job_id=b"rq_job_id_123",
            s_last_updated_at=b"20191225044444",
        )

        builder_id = self._insert_builder()
        self._insert_selection(
            1, "text/tab-separated-values", builder_id=builder_id, has_errors=False
        )

        logic_builder.handle_zim_generation(
            redis, self.wp10db, builder_id, "test_title", "a", "zz", user_id=1234
        )

        mock_create_zimfarm_schedule.assert_called_once_with(
            redis, self.wp10db, self.builder, "test_title", "a", "zz"
        )
        mock_request_zimfarm_task.assert_called_once_with(
            redis, self.wp10db, self.builder
        )
        with self.wp10db.cursor() as cursor:
            cursor.execute(
                "SELECT z_task_id, z_status, z_requested_at"
                " FROM zim_tasks"
                " WHERE z_selection_id = 1"
            )
            data = cursor.fetchone()
        self.assertEqual(b"1234-a", data["z_task_id"])
        self.assertEqual(b"REQUESTED", data["z_status"])
        self.assertEqual(b"20221225000102", data["z_requested_at"])

    @patch(
        "wp1.logic.builder.utcnow",
        return_value=datetime.datetime(2022, 12, 25, 0, 1, 2),
    )
    @patch("wp1.logic.builder.zimfarm.get_zimfarm_token", return_value="test_token")
    def test_handle_zim_generation_long_title(
        self, mock_utcnow, mock_get_zimfarm_token
    ):
        redis = MagicMock()
        s3 = MagicMock()

        builder_id = self._insert_builder()

        with self.assertRaises(InvalidZimTitleError):
            logic_builder.handle_zim_generation(
                redis, self.wp10db, builder_id, "A" * 31, "a", "z", user_id=1234
            )

    @patch("wp1.logic.builder.zimfarm.request_zimfarm_task")
    def test_handle_zim_generation_404(self, mock_request_zimfarm_task):
        redis = MagicMock()
        s3 = MagicMock()
        mock_request_zimfarm_task.return_value = "1234-a"

        with self.assertRaises(ObjectNotFoundError):
            logic_builder.handle_zim_generation(
                redis, self.wp10db, "404builder", "Title", "Description", user_id=1234
            )

    @patch("wp1.logic.builder.zimfarm.request_zimfarm_task")
    def test_handle_zim_generation_not_authorized(self, mock_request_zimfarm_task):
        redis = MagicMock()
        mock_request_zimfarm_task.return_value = "1234-a"

        builder_id = self._insert_builder()
        self._insert_selection(
            1, "text/tab-separated-values", builder_id=builder_id, has_errors=False
        )

        with self.assertRaises(UserNotAuthorizedError):
            logic_builder.handle_zim_generation(
                redis, self.wp10db, builder_id, "Title", "Description", user_id=5678
            )

    @patch("wp1.logic.builder.zimfarm.create_or_update_zimfarm_schedule")
    @patch("wp1.logic.builder.zimfarm.request_zimfarm_task")
    @patch("wp1.logic.zim_schedules.schedule_future_zimfile_generations")
    @patch("wp1.logic.builder.zimfarm.zimfarm_schedule_exists", return_value=True)
    @patch(
        "wp1.logic.builder.utcnow",
        return_value=datetime.datetime(2022, 12, 25, 0, 1, 2),
    )
    def test_handle_zim_generation_with_existing_schedule_update(
        self,
        mock_utcnow,
        mock_zimfarm_schedule_exists,
        mock_schedule_future,
        mock_request_zimfarm_task,
        mock_update_schedule,
    ):
        """Test handle_zim_generation when existing schedule exists and needs updating."""
        redis = MagicMock()

        builder_id = self._insert_builder()
        self._insert_selection(1, "text/tab-separated-values", builder_id=builder_id)
        self._insert_zim_schedule(
            schedule_id=b"schedule_123",
            builder_id=builder_id,
            rq_job_id=b"rq_job_id_123",
            last_updated_at=b"20191225044444",
            remaining_generations=0,
        )

        mock_request_zimfarm_task.return_value = "1234-a"
        mock_update_schedule.return_value = ZimSchedule(
            s_id=b"schedule_123",
            s_builder_id=b"1a-2b-3c-4d",
            s_rq_job_id=b"rq_job_id_123",
            s_last_updated_at=b"20191225044444",
        )

        result = logic_builder.handle_zim_generation(
            redis,
            self.wp10db,
            builder_id,
            user_id=1234,
            title="Updated Title",
            description="Updated Description",
            long_description="Updated Long Description",
            scheduled_repetitions=5,
        )

        mock_update_schedule.assert_called_once_with(
            redis,
            self.wp10db,
            self.builder,
            "Updated Title",
            "Updated Description",
            "Updated Long Description",
        )
        mock_request_zimfarm_task.assert_called_once_with(
            redis, self.wp10db, self.builder
        )
        mock_schedule_future.assert_called_once_with(
            redis, self.wp10db, self.builder, b"schedule_123", 5
        )

        self.assertEqual(b"1234-a", result)

    @patch("wp1.logic.builder.zimfarm.create_or_update_zimfarm_schedule")
    @patch("wp1.logic.builder.zimfarm.request_zimfarm_task")
    @patch("wp1.logic.builder.zimfarm.zimfarm_schedule_exists", return_value=True)
    @patch(
        "wp1.logic.builder.utcnow",
        return_value=datetime.datetime(2022, 12, 25, 0, 1, 2),
    )
    def test_handle_zim_generation_create_new_schedule(
        self,
        mock_utcnow,
        mock_zimfarm_schedule_exists,
        mock_request_zimfarm_task,
        mock_create_schedule,
    ):
        """Test handle_zim_generation when no existing schedule exists, creates new one."""
        redis = MagicMock()

        builder_id = self._insert_builder()
        self._insert_selection(1, "text/tab-separated-values", builder_id=builder_id)

        mock_request_zimfarm_task.return_value = "1234-a"
        mock_create_schedule.return_value = ZimSchedule(
            s_id=b"schedule_123",
            s_builder_id=b"1a-2b-3c-4d",
            s_rq_job_id=b"rq_job_id_123",
            s_last_updated_at=b"20191225044444",
        )

        result = logic_builder.handle_zim_generation(
            redis,
            self.wp10db,
            builder_id,
            user_id=1234,
            title="New Title",
            description="New Description",
            long_description="New Long Description",
        )

        mock_create_schedule.assert_called_once_with(
            redis,
            self.wp10db,
            self.builder,
            "New Title",
            "New Description",
            "New Long Description",
        )
        mock_request_zimfarm_task.assert_called_once_with(
            redis, self.wp10db, self.builder
        )

        self.assertEqual(b"1234-a", result)

    def test_update_version_for_finished_zim(self):
        builder_id = self._insert_builder(zim_version=1)
        self._insert_selection(
            1,
            "text/tab-separated-values",
            version=1,
            builder_id=builder_id,
            has_errors=False,
            zim_file_ready=True,
        )
        self._insert_selection(
            2,
            "text/tab-separated-values",
            version=2,
            builder_id=builder_id,
            has_errors=False,
            zim_task_id="9abc",
            zim_file_ready=True,
        )

        logic_builder.update_version_for_finished_zim(self.wp10db, "9abc")

        with self.wp10db.cursor() as cursor:
            cursor.execute(
                "SELECT b.b_selection_zim_version " "FROM builders b WHERE b.b_id = %s",
                builder_id,
            )
            data = cursor.fetchone()

        self.assertEqual(2, data["b_selection_zim_version"])

    @patch("wp1.logic.builder.handle_zim_generation")
    def test_auto_handle_zim_generation(self, mock_handle_zim_generation):
        redis = MagicMock()
        builder_id = self._insert_builder(zim_version=1)
        self._insert_selection(
            1,
            "text/tab-separated-values",
            version=1,
            builder_id=builder_id,
            has_errors=False,
            zim_file_ready=True,
        )
        self._insert_zim_schedule(b"schedule_123", builder_id, b"rq_job_id_123")

        logic_builder.auto_handle_zim_generation(redis, self.wp10db, builder_id)

        mock_handle_zim_generation.assert_called_once_with(
            redis,
            self.wp10db,
            builder_id,
            title=None,
            description=None,
            long_description=None,
        )

    @patch("wp1.logic.builder.handle_zim_generation")
    @patch("wp1.logic.builder.zimfarm.cancel_zim_by_task_id")
    def test_auto_handle_zim_generation_zimfarm_error(
        self, mock_cancel_zim, mock_handle_zim_generation
    ):
        redis = MagicMock()
        mock_cancel_zim.side_effect = ZimFarmError
        builder_id = self._insert_builder(zim_version=1)
        self._insert_selection(
            1,
            "text/tab-separated-values",
            version=1,
            builder_id=builder_id,
            has_errors=False,
            zim_file_ready=True,
        )
        self._insert_zim_schedule(b"schedule_123", builder_id, b"rq_job_id_123")

        logic_builder.auto_handle_zim_generation(redis, self.wp10db, builder_id)

        mock_handle_zim_generation.assert_called_once_with(
            redis,
            self.wp10db,
            builder_id,
            title=None,
            description=None,
            long_description=None,
        )

    @patch("wp1.logic.builder.handle_zim_generation")
    @patch("wp1.logic.builder.zimfarm.cancel_zim_by_task_id")
    def test_auto_handle_zim_generation_cancel_tasks(
        self, mock_cancel_zim, mock_handle_zim_generation
    ):
        redis = MagicMock()
        builder_id = self._insert_builder(zim_version=3)
        self._insert_selection(
            1,
            "text/tab-separated-values",
            version=1,
            builder_id=builder_id,
            has_errors=False,
            zim_task_id="5678",
            zim_file_ready=True,
        )
        self._insert_selection(
            2,
            "text/tab-separated-values",
            version=2,
            builder_id=builder_id,
            has_errors=False,
            zim_task_id="1abc",
            zim_file_ready=False,
        )
        self._insert_selection(
            3,
            "text/tab-separated-values",
            version=3,
            builder_id=builder_id,
            has_errors=False,
            zim_task_id="9def",
            zim_file_ready=False,
        )
        self._insert_zim_schedule(
            b"schedule_123",
            builder_id,
            b"rq_job_id_123",
            title=b"Title",
            description=b"A desc",
            long_description=b"Long desc",
        )

        with self.wp10db.cursor() as cursor:
            cursor.execute(
                """UPDATE zim_tasks z
                        JOIN selections s
                          ON s.s_id = z.z_selection_id
                        SET z.z_status = "REQUESTED"
                        WHERE s.s_id IN (2,3)"""
            )
        logic_builder.auto_handle_zim_generation(redis, self.wp10db, builder_id)

        mock_cancel_zim.assert_has_calls(
            (call(redis, "1abc"), call(redis, "9def")), any_order=True
        )

        mock_handle_zim_generation.assert_called_once_with(
            redis,
            self.wp10db,
            builder_id,
            title="Title",
            description="A desc",
            long_description="Long desc",
        )

        with self.wp10db.cursor() as cursor:
            cursor.execute(
                'SELECT COUNT(*) as cnt FROM zim_tasks z WHERE z.z_status = "REQUESTED"'
            )
            count = cursor.fetchone()["cnt"]

        self.assertEqual(0, count)

    def test_pending_zim_tasks_for(self):
        builder_id = self._insert_builder(zim_version=1)
        self._insert_selection(
            1,
            "text/tab-separated-values",
            version=1,
            builder_id=builder_id,
            has_errors=False,
            zim_task_id="5678",
            zim_file_ready=True,
        )
        self._insert_selection(
            2,
            "text/tab-separated-values",
            version=2,
            builder_id=builder_id,
            has_errors=False,
            zim_task_id="1abc",
            zim_file_ready=False,
        )
        self._insert_selection(
            3,
            "text/tab-separated-values",
            version=3,
            builder_id=builder_id,
            has_errors=False,
            zim_task_id="9def",
            zim_file_ready=False,
        )

        with self.wp10db.cursor() as cursor:
            cursor.execute(
                """UPDATE zim_tasks z
                        JOIN selections s
                          ON s.s_id = z.z_selection_id
                        SET z.z_status = "REQUESTED"
                        WHERE s.s_id IN (2,3)"""
            )

        tasks = logic_builder.pending_zim_tasks_for(self.wp10db, builder_id)
        self.assertIsNotNone(tasks)
        self.assertEqual(2, len(tasks))
        self.assertIn("1abc", tasks)
        self.assertIn("9def", tasks)

    @patch("wp1.logic.builder.zimfarm.request_zimfarm_task")
    @patch("wp1.logic.builder.wp10_connect")
    @patch("wp1.logic.builder.redis_connect")
    @patch("wp1.logic.builder.connect_storage")
    @patch(
        "wp1.logic.builder.utcnow",
        return_value=datetime.datetime(2022, 12, 25, 0, 1, 2),
    )
    def test_request_zim_file_task_for_builder(
        self,
        mock_utcnow,
        mock_connect_storage,
        mock_redis_connect,
        mock_wp10_connect,
        mock_request_zimfarm_task,
    ):
        """Test basic zimfile request functionality"""
        self._insert_builder()
        self._insert_selection(
            1, "text/tab-separated-values", builder_id=self.builder.b_id
        )
        self._insert_zim_schedule(b"schedule_123", self.builder.b_id, b"rq_job_id_123")

        mock_wp10_connect.return_value = self.wp10db
        redis_mock = MagicMock()
        s3_mock = MagicMock()
        mock_redis_connect.return_value = redis_mock
        mock_connect_storage.return_value = s3_mock

        mock_request_zimfarm_task.return_value = "test_task_id_123"

        actual_zim_file = logic_builder.request_zim_file_task_for_builder(
            redis_mock,
            self.wp10db,
            builder=self.builder,
            zim_schedule_id="schedule_123",
        )

        self.assertEqual(b"test_task_id_123", actual_zim_file.z_task_id)
        mock_request_zimfarm_task.assert_called_once_with(
            redis_mock, self.wp10db, self.builder
        )

        with self.wp10db.cursor() as cursor:
            cursor.execute("SELECT * FROM zim_tasks WHERE z_selection_id = 1")
            zim_file = cursor.fetchone()
            self.assertEqual(b"REQUESTED", zim_file["z_status"])
            self.assertEqual(b"test_task_id_123", zim_file["z_task_id"])
            self.assertEqual(b"20221225000102", zim_file["z_requested_at"])

    @patch("wp1.logic.builder.materialize_builder")
    @patch("wp1.logic.builder.zimfarm.request_zimfarm_task")
    @patch("wp1.logic.builder.wp10_connect")
    @patch("wp1.logic.builder.redis_connect")
    @patch("wp1.logic.builder.connect_storage")
    @patch(
        "wp1.logic.builder.utcnow",
        return_value=datetime.datetime(2022, 12, 25, 0, 1, 2),
    )
    def test_request_scheduled_zim_file_for_builder(
        self,
        mock_utcnow,
        mock_connect_storage,
        mock_redis_connect,
        mock_wp10_connect,
        mock_request_zimfarm_task,
        mock_materialize_builder,
    ):
        """Test zimfile request with rebuild_selection=True"""
        self._insert_builder()
        self._insert_selection(
            1, "text/tab-separated-values", builder_id=self.builder.b_id
        )
        self._insert_zim_schedule(b"schedule_123", self.builder.b_id, b"rq_job_id_123")

        mock_wp10_connect.return_value = self.wp10db
        redis_mock = MagicMock()
        s3_mock = MagicMock()
        mock_redis_connect.return_value = redis_mock
        mock_connect_storage.return_value = s3_mock

        mock_request_zimfarm_task.return_value = "test_task_id_456"

        with patch("wp1.logic.builder.importlib.import_module") as mock_import:
            mock_module = MagicMock()
            mock_module.Builder = MagicMock()
            mock_import.return_value = mock_module

            actual_zim_file = logic_builder.request_scheduled_zim_file_for_builder(
                builder=self.builder, zim_schedule_id=b"schedule_123"
            )

        self.assertEqual(b"test_task_id_456", actual_zim_file.z_task_id)
        mock_materialize_builder.assert_called_once()
        mock_request_zimfarm_task.assert_called_once()

    @patch("wp1.logic.builder.importlib.import_module")
    @patch("wp1.logic.builder.wp10_connect")
    @patch("wp1.logic.builder.redis_connect")
    @patch("wp1.logic.builder.connect_storage")
    @patch(
        "wp1.logic.builder.utcnow",
        return_value=datetime.datetime(2022, 12, 25, 0, 1, 2),
    )
    def test_request_scheduled_zim_file_for_builder_missing_class(
        self,
        mock_utcnow,
        mock_connect_storage,
        mock_redis_connect,
        mock_wp10_connect,
        mock_import_module,
    ):
        """Test zimfile request with missing builder class in module"""
        self._insert_builder()
        self._insert_selection(
            1, "text/tab-separated-values", builder_id=self.builder.b_id
        )
        self._insert_zim_schedule(b"schedule_123", self.builder.b_id, b"rq_job_id_123")

        mock_wp10_connect.return_value = self.wp10db
        redis_mock = MagicMock()
        s3_mock = MagicMock()
        mock_redis_connect.return_value = redis_mock
        mock_connect_storage.return_value = s3_mock

        mock_module = MagicMock()
        mock_module.Builder = None  # Simulate missing Builder class
        mock_import_module.return_value = mock_module
        with self.assertRaises(ImportError) as cm:
            actual = logic_builder.request_scheduled_zim_file_for_builder(
                builder=self.builder, zim_schedule_id=b"schedule_123"
            )

    @patch("wp1.logic.builder.importlib.import_module")
    @patch("wp1.logic.builder.materialize_builder")
    @patch("wp1.logic.builder.zimfarm.request_zimfarm_task")
    @patch("wp1.logic.builder.zim_file_for_latest_selection")
    @patch("wp1.logic.builder.wp10_connect")
    @patch("wp1.logic.builder.redis_connect")
    @patch("wp1.logic.builder.connect_storage")
    @patch(
        "wp1.logic.zim_schedules.utcnow",
        return_value=datetime.datetime(2022, 12, 25, 0, 1, 2),
    )
    def test_request_scheduled_zim_file_for_builder_with_zim_schedule(
        self,
        mock_utcnow,
        mock_connect_storage,
        mock_redis_connect,
        mock_wp10_connect,
        mock_zim_file_for_latest_selection,
        mock_request_zimfarm_task,
        mock_materialize_builder,
        mock_import_module,
    ):
        """Test zimfile request with rebuild_selection=True"""
        self._insert_builder()
        self._insert_selection(
            1, "text/tab-separated-values", builder_id=self.builder.b_id
        )
        self._insert_zim_schedule(b"schedule_123", self.builder.b_id, b"rq_job_id_123")

        mock_wp10_connect.return_value = self.wp10db
        redis_mock = MagicMock()
        s3_mock = MagicMock()
        mock_redis_connect.return_value = redis_mock
        mock_connect_storage.return_value = s3_mock

        mock_request_zimfarm_task.return_value = "test_task_id_456"
        mock_zim_file_for_latest_selection.return_value = ZimTask(
            z_id=123, z_selection_id=1, z_zim_schedule_id=b"schedule_123"
        )

        mock_module = MagicMock()
        mock_builder_cls = MagicMock()
        mock_module.Builder = mock_builder_cls
        mock_import_module.return_value = mock_module

        actual_zim_file = logic_builder.request_scheduled_zim_file_for_builder(
            builder=self.builder, zim_schedule_id=b"schedule_123"
        )

        self.assertEqual(b"test_task_id_456", actual_zim_file.z_task_id)
        mock_materialize_builder.assert_called_once()
        mock_request_zimfarm_task.assert_called_once()

    @patch("wp1.logic.builder.zimfarm.request_zimfarm_task")
    @patch("wp1.logic.builder.wp10_connect")
    @patch("wp1.logic.builder.redis_connect")
    @patch("wp1.logic.builder.connect_storage")
    @patch(
        "wp1.logic.builder.utcnow",
        return_value=datetime.datetime(2022, 12, 25, 0, 1, 2),
    )
    def test_request_zim_file_task_for_builder_no_selection_found(
        self,
        mock_utcnow,
        mock_connect_storage,
        mock_redis_connect,
        mock_wp10_connect,
        mock_request_zimfarm_task,
    ):
        """Test zimfile request when no selection is found"""
        self._insert_builder()
        # Don't insert a selection to simulate missing selection

        mock_wp10_connect.return_value = self.wp10db
        redis_mock = MagicMock()
        s3_mock = MagicMock()
        mock_redis_connect.return_value = redis_mock
        mock_connect_storage.return_value = s3_mock

        mock_request_zimfarm_task.return_value = "test_task_id_no_selection"

        with self.assertRaises(Exception):
            logic_builder.request_zim_file_task_for_builder(
                redis=redis_mock,
                wp10db=self.wp10db,
                builder=self.builder.b_id,
                zim_schedule_id=b"schedule_123",
            )

        mock_request_zimfarm_task.assert_called_once()

    def test_get_builder_module_class_success(self):
        cls = logic_builder.get_builder_module_class("wp1.selection.models.simple")
        self.assertIs(cls, SimpleBuilder)

    def test_get_builder_module_class_no_builder_attribute(self):
        with self.assertRaises(ImportError) as cm:
            logic_builder.get_builder_module_class("nonexistent.module")
        self.assertIn("No module named", str(cm.exception))

    @patch("wp1.logic.builder.importlib.import_module")
    def test_get_builder_module_class_missing_builder_class(self, mock_import):
        mock_module = MagicMock()
        mock_module.Builder = None  # Simulate missing Builder class
        mock_import.return_value = mock_module
        with self.assertRaises(ImportError) as cm:
            logic_builder.get_builder_module_class("wp1.selection.models.simple")

        self.assertIn("Builder class not found in module", str(cm.exception))

    @patch("wp1.logic.builder.zimfarm.request_zimfarm_task")
    @patch(
        "wp1.logic.builder.utcnow", return_value=datetime.datetime(2025, 1, 2, 0, 0, 0)
    )
    def test_regenerate_zim_updates_old_task_when_selection_version_changed(
        self, mock_utcnow, mock_request_zimfarm_task
    ):
        """
        Ensure the existing zim_task is updated (not dupplicated) when the selection version changes.
        """
        self._insert_builder()
        zim_schedule_id = self._setup_failed_zim_regeneration_scenario(
            create_new_selection=True
        )

        mock_request_zimfarm_task.return_value = "new-task-id"

        redis = MagicMock()
        result = logic_builder.request_zim_file_task_for_builder(
            redis, self.wp10db, self.builder, zim_schedule_id=zim_schedule_id
        )

        with self.wp10db.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM zim_tasks")
            count = cursor.fetchone()["count"]
            cursor.execute("SELECT z_selection_id FROM zim_tasks")
            row = cursor.fetchone()

        self.assertEqual(1, count)
        self.assertEqual(b"2", row["z_selection_id"])

    @patch("wp1.logic.builder.zimfarm.request_zimfarm_task")
    @patch(
        "wp1.logic.builder.utcnow", return_value=datetime.datetime(2025, 1, 2, 0, 0, 0)
    )
    def test_regenerate_zim_saves_new_task_id(
        self, mock_utcnow, mock_request_zimfarm_task
    ):
        """
        test that new task_id from Zimfarm is saved correctly.
        """
        self._insert_builder()
        zim_schedule_id = self._setup_failed_zim_regeneration_scenario(
            old_task_id="task_v1"
        )

        mock_request_zimfarm_task.return_value = "task_v2"

        redis = MagicMock()
        result = logic_builder.request_zim_file_task_for_builder(
            redis, self.wp10db, self.builder, zim_schedule_id=zim_schedule_id
        )

        self.assertIsNotNone(result)
        self.assertEqual(b"task_v2", result.z_task_id)
        self.assertEqual(b"REQUESTED", result.z_status)

        with self.wp10db.cursor() as cursor:
            cursor.execute("SELECT z_task_id FROM zim_tasks WHERE z_selection_id = 1")
            row = cursor.fetchone()

        self.assertEqual(b"task_v2", row["z_task_id"])

    @patch("wp1.logic.builder.zimfarm.request_zimfarm_task")
    @patch(
        "wp1.logic.builder.utcnow", return_value=datetime.datetime(2025, 1, 2, 0, 0, 0)
    )
    def test_regenerate_zim_updates_b_selection_zim_version(
        self, mock_utcnow, mock_request_zimfarm_task
    ):
        """
        test that b_selection_zim_version is updated for downloads to work.
        """
        self._insert_builder(zim_version=1)
        zim_schedule_id = self._setup_failed_zim_regeneration_scenario(
            old_task_id="old-task", create_new_selection=True
        )

        with self.wp10db.cursor() as cursor:
            cursor.execute(
                "SELECT b_selection_zim_version FROM builders WHERE b_id = %s",
                (self.builder.b_id,),
            )
            version_before = cursor.fetchone()["b_selection_zim_version"]

        self.assertEqual(1, version_before)

        mock_request_zimfarm_task.return_value = "task_v2"

        redis = MagicMock()
        result = logic_builder.request_zim_file_task_for_builder(
            redis, self.wp10db, self.builder, zim_schedule_id=zim_schedule_id
        )

        with self.wp10db.cursor() as cursor:
            cursor.execute(
                "SELECT b_selection_zim_version FROM builders WHERE b_id = %s",
                (self.builder.b_id,),
            )
            version_after = cursor.fetchone()["b_selection_zim_version"]

        self.assertEqual(2, version_after)

    @patch("wp1.logic.builder.zimfarm.zim_file_url_for_task_id")
    def test_download_url_after_regeneration(self, mock_zim_file_url):
        """
        test that download URL works after regenerating a failed ZIM.
        """
        self._insert_builder()

        with self.wp10db.cursor() as cursor:
            # Selection v1 with failed ZIM
            cursor.execute(
                """INSERT INTO selections
                (s_id, s_builder_id, s_updated_at, s_content_type, s_version, s_object_key, s_article_count)
                VALUES (%s, %s, '20230101000000', 'text/tab-separated-values', 1, 'old.tsv', 100)""",
                (1, self.builder.b_id),
            )
            cursor.execute(
                """INSERT INTO zim_tasks
                (z_selection_id, z_status, z_task_id)
                VALUES (%s, 'FAILED', 'old-failed-task')""",
                (1,),
            )
            # Selection v2 with successful ZIM
            cursor.execute(
                """INSERT INTO selections
                (s_id, s_builder_id, s_updated_at, s_content_type, s_version, s_object_key, s_article_count)
                VALUES (%s, %s, '20230102000000', 'text/tab-separated-values', 2, 'new.tsv', 100)""",
                (2, self.builder.b_id),
            )
            cursor.execute(
                """INSERT INTO zim_tasks
                (z_selection_id, z_status, z_task_id)
                VALUES (%s, 'FILE_READY', 'new-successful-task')""",
                (2,),
            )
            cursor.execute(
                """UPDATE builders SET
                b_current_version = 2,
                b_selection_zim_version = 2
                WHERE b_id = %s""",
                (self.builder.b_id,),
            )
        self.wp10db.commit()

        mock_zim_file_url.return_value = "https://download.kiwix.org/zim/new-file.zim"

        url = logic_builder.latest_zim_file_url_for(self.wp10db, self.builder.b_id)

        self.assertIsNotNone(url)
        mock_zim_file_url.assert_called_once_with(b"new-successful-task")
