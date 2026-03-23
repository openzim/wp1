import unittest

from wp1.base_db_test import BaseWpOneDbTest
from wp1.logic import move as logic_move
from wp1.models.wp10.move import Move


class LogicMoveTest(BaseWpOneDbTest):

    def test_insert_duplicate_key_update(self):
        # Insert initial data using raw SQL
        with self.wp10db.cursor() as cursor:
            cursor.execute(
                """INSERT INTO moves
                   (m_timestamp, m_old_namespace, m_old_article,
                    m_new_namespace, m_new_article)
                 VALUES (%s, %s, %s, %s, %s)""",
                (b"20200101000000\x00\x00\x00\x00\x00\x00",
                 0, b"Old_Article_1", 0, b"New_Article_1"),
            )
        self.wp10db.commit()

        # Insert duplicate row using the code under test
        move2 = Move(
            m_timestamp=b"20200101000000\x00\x00\x00\x00\x00\x00",
            m_old_namespace=0,
            m_old_article=b"Old_Article_1",
            m_new_namespace=1,
            m_new_article=b"Different_Article",
        )
        logic_move.insert(self.wp10db, move2)
        self.wp10db.commit()

        # Verify the record was updated, not duplicated
        with self.wp10db.cursor() as cursor:
            cursor.execute(
                """SELECT * FROM moves
                 WHERE m_timestamp = %s
                   AND m_old_namespace = %s
                   AND m_old_article = %s""",
                (b"20200101000000\x00\x00\x00\x00\x00\x00", 0, b"Old_Article_1"),
            )
            updated_move = cursor.fetchone()
        self.assertIsNotNone(updated_move)
        self.assertEqual(updated_move["m_new_namespace"], 1)
        self.assertEqual(updated_move["m_new_article"], b"Different_Article")
