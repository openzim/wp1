import attr

from lucky.db_util import get_cursor_context
from lucky.models.wp10.log import Log

def insert_or_update(wp10db, log):
  with get_cursor_context(wp10db) as cursor:
    cursor.execute('''INSERT INTO ''' + Log.table_name + '''
      (l_project, l_namespace, l_article, l_action, l_timestamp, l_old, l_new,
       l_revision_timestamp)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      ON DUPLICATE KEY UPDATE l_article = l_article
    ''', attr.astuple(log))

