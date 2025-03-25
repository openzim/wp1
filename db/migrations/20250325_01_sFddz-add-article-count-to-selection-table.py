"""
Add article count to selection table
"""
from io import BytesIO

from yoyo import step

from wp1 import storage

__depends__ = {'20250120_01_4GEMs-convert-user-id-to-str'}


def update_article_counts(conn):
  s3 = storage.connect_storage()
  with conn.cursor() as cursor:
    cursor.execute(
        'SELECT s_id, s_object_key FROM selections WHERE s_article_count IS NULL'
    )
    for s_id, s_object_key in cursor.fetchall():
      buffer = BytesIO()
      s3.download_fileobj(s_object_key.decode('utf-8'), buffer)
      data = buffer.getvalue()
      article_count = data.count(b'\n') + 1
      cursor.execute(
          'UPDATE selections SET s_article_count = %s WHERE s_id = %s',
          (article_count, s_id))


steps = [
    step("ALTER TABLE selections ADD COLUMN s_article_count INT",
         "ALTER TABLE selections DROP COLUMN s_article_count"),
    step(update_article_counts, None),
]
