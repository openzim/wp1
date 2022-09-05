"""
Change params field in builders to longblob
"""
import json

from yoyo import step

__depends__ = {'20220818_01_5x0T9-add-object-key-column-to-selections'}


def remove_truncated_builders(conn):
  cursor = conn.cursor()
  cursor.execute('SELECT b_id, b_params FROM builders')
  data = cursor.fetchall()
  for row in data:
    try:
      json.loads(row[1])
    except json.decoder.JSONDecodeError:
      cursor.execute(
          '''DELETE builders, selections FROM builders
             LEFT JOIN selections ON builders.b_id = selections.s_builder_id
             WHERE builders.b_id = %s''', row[0])


steps = [
    step("ALTER TABLE builders CHANGE COLUMN b_params b_params LONGBLOB",
         "ALTER TABLE builders CHANGE COLUMN b_params b_params BLOB"),
    step(remove_truncated_builders)
]
