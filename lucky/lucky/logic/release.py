import logging
import time

from lucky.models.wp10.release import Release

logger = logging.getLogger(__name__)

def insert_or_update_release_data(
    wp10_session, page_title, category, timestamp):
  timestamp_binary = time.strftime(
    '%Y-%m-%dT%H:%M:%SZ', timestamp.timetuple()).encode('utf-8')

  release = wp10_session.query(Release).get(page_title)
  if release is None:
    logging.info('New article found: %s', page_title.decode('utf-8'))
    release = Release(
      article=page_title, category=category, timestamp=timestamp_binary)
  else:
    logging.info('Updating article: %s', page_title.decode('utf-8'))
    release.article = page_title
    release.category = category
    release.timestamp = timestamp_binary
  wp10_session.add(release)
