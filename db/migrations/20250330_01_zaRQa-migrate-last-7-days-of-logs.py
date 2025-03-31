"""
Migrate last 7 days of logs
"""
from datetime import timedelta

from yoyo import step

from wp1.logic import log as logic_log
from wp1.models.wp10.log import Log
from wp1.redis_db import connect as redis_connect
from wp1.time import get_current_datetime

__depends__ = {
    '20250120_01_4GEMs-convert-user-id-to-str',
    '20250323_01_xyzAB-add-temp-pageviews-table',
    '20250324_02_arj6b-add-ps-article-index-to-page-scores'
}


def migrate_logs(conn):
  redis = redis_connect()

  from_dt = get_current_datetime() - timedelta(days=7)
  from_dt.replace(hour=23, minute=59, second=59)

  n = 0
  print(f"Fetching logs from {from_dt} to now")
  with conn.cursor() as cursor:
    cursor.execute(f"""
        SELECT l_project, l_namespace, l_article, l_action,
            l_timestamp, l_old, l_new, l_revision_timestamp FROM logging
        WHERE l_timestamp >= '{from_dt}'
    """)
    for log_db in cursor.fetchall():
      log = Log(l_project=log_db[0],
                l_namespace=log_db[1],
                l_article=log_db[2],
                l_action=log_db[3],
                l_timestamp=log_db[4],
                l_old=log_db[5],
                l_new=log_db[6],
                l_revision_timestamp=log_db[7])
      logic_log.insert_or_update(redis, log)

      n += 1
      if n % 1000 == 0:
        print(f"Inserted {n} logs into Redis")


steps = [step(migrate_logs)]
