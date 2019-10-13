import logging
import os
import time

import pymysql
import pymysql.cursors
import pymysql.err

logger = logging.getLogger(__name__)

RETRY_TIME_SECONDS = 5

try:
  from wp1.credentials import WP10_CREDS

  def connect():
    kwargs = {
        'charset': None,
        'use_unicode': False,
        'cursorclass': pymysql.cursors.DictCursor,
        **WP10_CREDS
    }

    tries = 4
    while True:
      try:
        return pymysql.connect(**kwargs)
      except pymysql.err.InternalError:
        if tries > 0:
          logging.warning(
              'Could not connect to database, retrying in %s seconds',
              RETRY_TIME_SECONDS)
          time.sleep(RETRY_TIME_SECONDS)
          tries -= 1
        else:
          raise

except ImportError:
  print('import error')

  # No creds, so return an empty connect method that will blow up. This is only
  # to satisfy imports.
  def connect():
    return None
