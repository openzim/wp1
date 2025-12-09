from wp1.base_db_test import BaseWpOneDbTest
from wp1.logic.zim_files import get_zim_task, get_zim_task_by_task_id
from wp1.models.wp10.zim_file import ZimTask


class ZimTasksTest(BaseWpOneDbTest):

    def setUp(self):
        super().setUp()
        self.test_zim_task_id = 1234
        self.test_zim_task_data = {
            "z_id": self.test_zim_task_id,
            "z_selection_id": b"test-selection-id",
            "z_zim_schedule_id": b"schedule-123",
            "z_status": b"COMPLETED",
            "z_task_id": b"test-task-id",
            "z_requested_at": None,
            "z_updated_at": None,
        }

    def test_get_zim_file(self):
        """Test successful retrieval of a ZIM file."""
        with self.wp10db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO zim_tasks (
                    z_id, z_selection_id, z_zim_schedule_id, z_status,
                    z_task_id, z_requested_at, z_updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    self.test_zim_task_data["z_id"],
                    self.test_zim_task_data["z_selection_id"],
                    self.test_zim_task_data["z_zim_schedule_id"],
                    self.test_zim_task_data["z_status"],
                    self.test_zim_task_data["z_task_id"],
                    self.test_zim_task_data["z_requested_at"],
                    self.test_zim_task_data["z_updated_at"],
                ),
            )

        result = get_zim_task(self.wp10db, self.test_zim_task_id)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, ZimTask)
        self.assertEqual(result.z_id, self.test_zim_task_id)
        self.assertEqual(
            result.z_selection_id, self.test_zim_task_data["z_selection_id"]
        )
        self.assertEqual(
            result.z_zim_schedule_id, self.test_zim_task_data["z_zim_schedule_id"]
        )
        self.assertEqual(result.z_status, self.test_zim_task_data["z_status"])
        self.assertEqual(result.z_task_id, self.test_zim_task_data["z_task_id"])

    def test_get_zim_file_not_found(self):
        """Test retrieval of a non-existent ZIM file."""
        non_existent_id = b"non-existent-id"
        result = get_zim_task(self.wp10db, non_existent_id)
        self.assertIsNone(result)

    def test_get_zim_file_with_null_fields(self):
        """Test retrieval of a ZIM file with some null fields."""
        zim_file_data_with_nulls = {
            "z_id": 1234,
            "z_selection_id": b"test-selection-id-2",
            "z_zim_schedule_id": b"schedule-123",
            "z_status": b"IN_PROGRESS",
            "z_task_id": None,  # Null task_id
            "z_requested_at": None,
            "z_updated_at": None,
        }

        with self.wp10db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO zim_tasks (
                    z_id, z_selection_id, z_zim_schedule_id, z_status,
                    z_task_id, z_requested_at, z_updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    zim_file_data_with_nulls["z_id"],
                    zim_file_data_with_nulls["z_selection_id"],
                    zim_file_data_with_nulls["z_zim_schedule_id"],
                    zim_file_data_with_nulls["z_status"],
                    zim_file_data_with_nulls["z_task_id"],
                    zim_file_data_with_nulls["z_requested_at"],
                    zim_file_data_with_nulls["z_updated_at"],
                ),
            )

        result = get_zim_task(self.wp10db, zim_file_data_with_nulls["z_id"])

        self.assertIsNotNone(result)
        self.assertIsInstance(result, ZimTask)
        self.assertEqual(zim_file_data_with_nulls["z_id"], result.z_id)
        self.assertEqual(
            zim_file_data_with_nulls["z_selection_id"], result.z_selection_id
        )
        self.assertEqual(
            zim_file_data_with_nulls["z_zim_schedule_id"], result.z_zim_schedule_id
        )
        self.assertEqual(zim_file_data_with_nulls["z_status"], result.z_status)
        self.assertIsNone(result.z_task_id)

    def test_get_zim_file_multiple_records(self):
        """Test that get_zim_file returns the correct record when multiple exist."""
        zim_file_1_data = {
            "z_id": 1234,
            "z_selection_id": b"test-selection-1",
            "z_zim_schedule_id": b"schedule-123",
            "z_status": b"COMPLETED",
            "z_task_id": b"test-task-1",
            "z_requested_at": None,
            "z_updated_at": None,
        }
        zim_file_2_data = {
            "z_id": 4321,
            "z_selection_id": b"test-selection-2",
            "z_zim_schedule_id": b"schedule-123",
            "z_status": b"IN_PROGRESS",
            "z_task_id": b"test-task-2",
            "z_requested_at": None,
            "z_updated_at": None,
        }

        with self.wp10db.cursor() as cursor:
            # Insert first record
            cursor.execute(
                """
                INSERT INTO zim_tasks (
                    z_id, z_selection_id, z_zim_schedule_id, z_status,
                    z_task_id, z_requested_at, z_updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    zim_file_1_data["z_id"],
                    zim_file_1_data["z_selection_id"],
                    zim_file_1_data["z_zim_schedule_id"],
                    zim_file_1_data["z_status"],
                    zim_file_1_data["z_task_id"],
                    zim_file_1_data["z_requested_at"],
                    zim_file_1_data["z_updated_at"],
                ),
            )

            # Insert second record
            cursor.execute(
                """
                INSERT INTO zim_tasks (
                    z_id, z_selection_id, z_zim_schedule_id, z_status,
                    z_task_id, z_requested_at, z_updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    zim_file_2_data["z_id"],
                    zim_file_2_data["z_selection_id"],
                    zim_file_2_data["z_zim_schedule_id"],
                    zim_file_2_data["z_status"],
                    zim_file_2_data["z_task_id"],
                    zim_file_2_data["z_requested_at"],
                    zim_file_2_data["z_updated_at"],
                ),
            )

        result_1 = get_zim_task(self.wp10db, zim_file_1_data["z_id"])
        self.assertIsNotNone(result_1)
        self.assertEqual(zim_file_1_data["z_id"], result_1.z_id)

        result_2 = get_zim_task(self.wp10db, zim_file_2_data["z_id"])
        self.assertIsNotNone(result_2)
        self.assertEqual(zim_file_2_data["z_id"], result_2.z_id)

    def test_get_zim_task_by_task_id(self):
        """Test successful retrieval of a ZIM task by its task ID."""
        with self.wp10db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO zim_tasks (
                    z_id, z_selection_id, z_zim_schedule_id, z_status,
                    z_task_id, z_requested_at, z_updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    self.test_zim_task_data["z_id"],
                    self.test_zim_task_data["z_selection_id"],
                    self.test_zim_task_data["z_zim_schedule_id"],
                    self.test_zim_task_data["z_status"],
                    self.test_zim_task_data["z_task_id"],
                    self.test_zim_task_data["z_requested_at"],
                    self.test_zim_task_data["z_updated_at"],
                ),
            )

        result = get_zim_task_by_task_id(
            self.wp10db, self.test_zim_task_data["z_task_id"]
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ZimTask)
        self.assertEqual(result.z_task_id, self.test_zim_task_data["z_task_id"])
        self.assertEqual(result.z_id, self.test_zim_task_data["z_id"])

    def test_get_zim_task_by_task_id_not_found(self):
        """Test retrieval of a ZIM task by a non-existent task ID."""
        non_existent_task_id = b"no-such-task-id"
        result = get_zim_task_by_task_id(self.wp10db, non_existent_task_id)
        self.assertIsNone(result)

    def test_get_zim_task_by_task_id_with_null_fields(self):
        """Test retrieval by task ID where some fields are null."""
        zim_file_data_with_nulls = {
            "z_id": 5678,
            "z_selection_id": b"test-selection-id-3",
            "z_zim_schedule_id": b"schedule-456",
            "z_status": b"FAILED",
            "z_task_id": b"null-task-id",
            "z_requested_at": None,
            "z_updated_at": None,
        }
        with self.wp10db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO zim_tasks (
                    z_id, z_selection_id, z_zim_schedule_id, z_status,
                    z_task_id, z_requested_at, z_updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    zim_file_data_with_nulls["z_id"],
                    zim_file_data_with_nulls["z_selection_id"],
                    zim_file_data_with_nulls["z_zim_schedule_id"],
                    zim_file_data_with_nulls["z_status"],
                    zim_file_data_with_nulls["z_task_id"],
                    zim_file_data_with_nulls["z_requested_at"],
                    zim_file_data_with_nulls["z_updated_at"],
                ),
            )

        result = get_zim_task_by_task_id(
            self.wp10db, zim_file_data_with_nulls["z_task_id"]
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.z_id, zim_file_data_with_nulls["z_id"])
        self.assertEqual(result.z_task_id, zim_file_data_with_nulls["z_task_id"])

    def test_get_zim_task_by_task_id_multiple_records(self):
        """Test that get_zim_task_by_task_id returns the correct record when multiple exist."""
        zim_file_1_data = {
            "z_id": 1001,
            "z_selection_id": b"sel-1",
            "z_zim_schedule_id": b"sched-1",
            "z_status": b"QUEUED",
            "z_task_id": b"task-1",
            "z_requested_at": None,
            "z_updated_at": None,
        }
        zim_file_2_data = {
            "z_id": 1002,
            "z_selection_id": b"sel-2",
            "z_zim_schedule_id": b"sched-2",
            "z_status": b"RUNNING",
            "z_task_id": b"task-2",
            "z_requested_at": None,
            "z_updated_at": None,
        }
        with self.wp10db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO zim_tasks (
                    z_id, z_selection_id, z_zim_schedule_id, z_status,
                    z_task_id, z_requested_at, z_updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    zim_file_1_data["z_id"],
                    zim_file_1_data["z_selection_id"],
                    zim_file_1_data["z_zim_schedule_id"],
                    zim_file_1_data["z_status"],
                    zim_file_1_data["z_task_id"],
                    zim_file_1_data["z_requested_at"],
                    zim_file_1_data["z_updated_at"],
                ),
            )
            cursor.execute(
                """
                INSERT INTO zim_tasks (
                    z_id, z_selection_id, z_zim_schedule_id, z_status,
                    z_task_id, z_requested_at, z_updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    zim_file_2_data["z_id"],
                    zim_file_2_data["z_selection_id"],
                    zim_file_2_data["z_zim_schedule_id"],
                    zim_file_2_data["z_status"],
                    zim_file_2_data["z_task_id"],
                    zim_file_2_data["z_requested_at"],
                    zim_file_2_data["z_updated_at"],
                ),
            )

        result_1 = get_zim_task_by_task_id(self.wp10db, zim_file_1_data["z_task_id"])
        self.assertIsNotNone(result_1)
        self.assertEqual(zim_file_1_data["z_id"], result_1.z_id)
        self.assertEqual(zim_file_1_data["z_task_id"], result_1.z_task_id)

        result_2 = get_zim_task_by_task_id(self.wp10db, zim_file_2_data["z_task_id"])
        self.assertIsNotNone(result_2)
        self.assertEqual(zim_file_2_data["z_id"], result_2.z_id)
        self.assertEqual(zim_file_2_data["z_task_id"], result_2.z_task_id)
