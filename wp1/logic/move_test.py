import unittest

from wp1.base_db_test import BaseWpOneDbTest
from wp1.logic import move as logic_move
from wp1.models.wp10.move import Move


class LogicMoveTest(BaseWpOneDbTest):

    def setUp(self):
        super().setUp()
        self.move1 = Move(
            m_timestamp=b"20200101000000\x00\x00\x00\x00\x00\x00",
            m_old_namespace=0,
            m_old_article=b"Old_Article_1",
            m_new_namespace=0,
            m_new_article=b"New_Article_1",
        )

    def test_insert_duplicate_key_update(self):
        logic_move.insert(self.wp10db, self.move1)
        self.wp10db.commit()

        inserted_move = logic_move.get_move(
            self.wp10db,
            self.move1.m_timestamp,
            self.move1.m_old_namespace,
            self.move1.m_old_article,
        )
        self.assertIsNotNone(inserted_move)
        self.assertEqual(inserted_move.m_new_namespace, 0)
        self.assertEqual(inserted_move.m_new_article, b"New_Article_1")

        #add duplicate row
        move2 = Move(
            m_timestamp=self.move1.m_timestamp,
            m_old_namespace=self.move1.m_old_namespace,
            m_old_article=self.move1.m_old_article,
            m_new_namespace=1,
            m_new_article=b"Different_Article",
        )
        logic_move.insert(self.wp10db, move2)
        self.wp10db.commit()

        # Verify the record was updated, not duplicated
        updated_move = logic_move.get_move(
            self.wp10db,
            self.move1.m_timestamp,
            self.move1.m_old_namespace,
            self.move1.m_old_article,
        )
        self.assertIsNotNone(updated_move)
        self.assertEqual(updated_move.m_new_namespace, 1)
        self.assertEqual(updated_move.m_new_article, b"Different_Article")
