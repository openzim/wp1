from contextlib import contextmanager

import pymysql.connections

def get_cursor_context(conn, *args, **kwargs):
  if isinstance(conn, pymysql.connections.Connection):
    return conn.cursor(*args, **kwargs)
  else:
    @contextmanager
    def get_cursor():
      cursor = conn.cursor(*args, **kwargs)
      try:
        yield cursor
      finally:
        cursor.close()

    return get_cursor()
