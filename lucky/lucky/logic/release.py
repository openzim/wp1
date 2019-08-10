import logging
import time

import attr

from lucky.models.wp10.release import Release

logger = logging.getLogger(__name__)

def insert_or_update_release_data(
    wp10db, page_title, category, timestamp):
  timestamp_binary = time.strftime(
    '%Y-%m-%dT%H:%M:%SZ', timestamp.timetuple()).encode('utf-8')
  release = Release(
    rel_article=page_title,
    rel_0p5_category=category,
    rel_0p5_timestamp=timestamp_binary)

  with wp10db.cursor() as cursor:
    cursor.execute('UPDATE ' + Release.table_name + ''' SET
        rel_article = %(rel_article)s, rel_0p5_category = %(rel_0p5_category)s,
        rel_0p5_timestamp = %(rel_0p5_timestamp)s
      WHERE rel_article = %(rel_article)s
    ''', attr.asdict(release))
    if cursor.rowcount == 0:
      logger.debug('No update for release, inserting')
      cursor.execute('INSERT INTO ' + Release.table_name + '''
          (rel_article, rel_0p5_category, rel_0p5_timestamp)
        VALUES
          (%(rel_article)s, %(rel_0p5_category)s, %(rel_0p5_timestamp)s)
        ON DUPLICATE KEY UPDATE rel_0p5_timestamp = %(rel_0p5_timestamp)s
      ''', attr.asdict(release))

def get_title_to_release(wp10db):
  logger.info('Querying release data')
  with wp10db.cursor() as cursor:
    cursor.execute('SELECT * FROM ' + Release.table_name)
    db_releases = cursor.fetchall()
  releases = [Release(**db_release) for db_release in db_releases]
  return dict((release.rel_article, release) for release in releases)
