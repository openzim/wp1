import unittest

from wp1.base_db_test import BaseWpOneDbTest
from wp1.logic import users as logic_users


class UsersTest(BaseWpOneDbTest):

    def test_create_or_update_user_inserts_new_user(self):
        logic_users.create_or_update_user(
            self.wp10db, "user_12345", "test_user", "test@example.com"
        )

        with self.wp10db.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE u_id = %s", ("user_12345",))
            row = cursor.fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(b"user_12345", row["u_id"])
        self.assertEqual(b"test_user", row["u_username"])
        self.assertEqual(b"test@example.com", row["u_email"])

    def test_create_or_update_user_updates_existing_user(self):
        # First insert
        logic_users.create_or_update_user(
            self.wp10db, "user_12345", "old_user", "old@example.com"
        )
        # Update with same user_id
        logic_users.create_or_update_user(
            self.wp10db, "user_12345", "new_user", "new@example.com"
        )

        with self.wp10db.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE u_id = %s", ("user_12345",))
            row = cursor.fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(b"user_12345", row["u_id"])
        self.assertEqual(b"new_user", row["u_username"])
        self.assertEqual(b"new@example.com", row["u_email"])

    def test_create_or_update_user_handles_none_email(self):
        logic_users.create_or_update_user(
            self.wp10db, "user_no_email", "no_email_user", None
        )

        with self.wp10db.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE u_id = %s", ("user_no_email",))
            row = cursor.fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(b"user_no_email", row["u_id"])
        self.assertEqual(b"no_email_user", row["u_username"])
        self.assertIsNone(row["u_email"])

    def test_create_or_update_user_updates_none_email_to_value(self):
        # Insert with None email
        logic_users.create_or_update_user(self.wp10db, "user_12345", "test_user", None)
        # Update to have email
        logic_users.create_or_update_user(
            self.wp10db, "user_12345", "test_user", "now_has_email@example.com"
        )

        with self.wp10db.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE u_id = %s", ("user_12345",))
            row = cursor.fetchone()

        self.assertEqual(b"now_has_email@example.com", row["u_email"])

    def test_user_exists_returns_true_when_user_exists(self):
        logic_users.create_or_update_user(
            self.wp10db, "existing_user", "test_user", "test@example.com"
        )

        result = logic_users.user_exists(self.wp10db, "existing_user")

        self.assertTrue(result)

    def test_user_exists_returns_false_when_user_does_not_exist(self):
        result = logic_users.user_exists(self.wp10db, "nonexistent_user")

        self.assertFalse(result)

    def test_user_exists_after_update(self):
        logic_users.create_or_update_user(
            self.wp10db, "user_12345", "old_user", "old@example.com"
        )
        logic_users.create_or_update_user(
            self.wp10db, "user_12345", "new_user", "new@example.com"
        )

        result = logic_users.user_exists(self.wp10db, "user_12345")

        self.assertTrue(result)

        # verify that only one row exists in db
        with self.wp10db.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) as cnt FROM users WHERE u_id = %s", ("user_12345",)
            )
            count = cursor.fetchone()["cnt"]

        self.assertEqual(1, count)
