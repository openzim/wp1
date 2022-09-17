"""
Change builder id column
"""
import uuid

from yoyo import step

__depends__ = {'20220904_01_sroTV-change-params-field-in-builders-to-longblob'}


def update_builder_id(conn):
  cursor = conn.cursor()
  cursor.execute('SELECT b_id FROM builders')
  for row in cursor.fetchall():
    new_id = str(uuid.uuid4()).encode('utf-8')
    cursor.execute('UPDATE builders SET b_id = %s WHERE b_id = %s',
                   (new_id, row[0]))
    cursor.execute(
        'UPDATE selections SET s_builder_id = %s WHERE s_builder_id = %s',
        (new_id, row[0]))


def restore_builder_id(conn):
  cursor = conn.cursor()
  cursor.execute('SELECT b_id FROM builders ORDER BY b_created_at')
  for id_, row in enumerate(cursor.fetchall()):
    cursor.execute('UPDATE builders SET b_id = %s WHERE b_id = %s',
                   (id_ + 1, row[0]))
    cursor.execute(
        'UPDATE selections SET s_builder_id = %s WHERE s_builder_id = %s',
        (id_ + 1, row[0]))


steps = [
    step(
        "ALTER TABLE builders CHANGE COLUMN b_id b_id VARBINARY(255) NOT NULL",
        "ALTER TABLE builders CHANGE COLUMN b_id b_id INTEGER NOT NULL AUTO_INCREMENT"
    ),
    step(
        "ALTER TABLE selections CHANGE COLUMN s_builder_id s_builder_id VARBINARY(255) NOT NULL",
        "ALTER TABLE selections CHANGE COLUMN s_builder_id s_builder_id INTEGER NOT NULL"
    ),
    step(update_builder_id, restore_builder_id),
]
