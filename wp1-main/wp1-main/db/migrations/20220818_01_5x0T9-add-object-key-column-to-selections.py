"""
Add object_key column to selections
"""

from yoyo import group, step

import wp1.logic.selection as logic_selection
from wp1.redis_db import connect
from wp1.selection.models.simple import Builder as SimpleBuilder
from wp1 import queues

__depends__ = {'20220813_02_Yqp7y-add-version-column-to-selections'}


def add_object_keys(conn):
  cursor = conn.cursor()
  cursor.execute('''SELECT s.s_id, s.s_content_type, b.b_model, b.b_name
                    FROM selections AS s JOIN builders AS b ON s.s_builder_id = b.b_id
            ''')
  data = cursor.fetchall()
  for row in data:
    object_key = logic_selection.object_key_for(row[0].decode('utf-8'),
                                                row[1].decode('utf-8'),
                                                row[2].decode('utf-8'),
                                                name=row[3].decode('utf-8'),
                                                use_legacy_schema=True)
    cursor.execute(
        '''UPDATE selections
           SET s_object_key = %s WHERE s_id = %s''', (object_key, row[0]))


def re_materialize_builders(conn):
  redis = connect()

  cursor = conn.cursor()
  cursor.execute('''SELECT b_id FROM builders''')
  data = cursor.fetchall()
  for row in data:
    queues.enqueue_materialize(redis, SimpleBuilder, row[0],
                               'text/tab-separated-values')


steps = [
    step(
        "ALTER TABLE selections ADD COLUMN (s_object_key VARBINARY(255) NOT NULL)",
        "ALTER TABLE selections DROP COLUMN s_object_key"),
    step(add_object_keys),
    step(re_materialize_builders),
]
