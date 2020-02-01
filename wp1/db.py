import logging
import os
import time

import pymysql
import pymysql.cursors
import pymysql.err

from wp1.credentials import CREDENTIALS, ENV

logger = logging.getLogger(__name__)

RETRY_TIME_SECONDS = 5


def connect(db_name):
  print(CREDENTIALS)
  print(ENV)

  creds = CREDENTIALS[ENV].get(db_name)
  if creds is None:
    raise ValueError('db credentials for %r in ENV=%s are None')

  kwargs = {
      'charset': None,
      'use_unicode': False,
      'cursorclass': pymysql.cursors.SSDictCursor,
      **creds
  }

  tries = 4
  while True:
    try:
      return pymysql.connect(**kwargs)
    except pymysql.err.InternalError:
      if tries > 0:
        logging.warning('Could not connect to database, retrying in %s seconds',
                        RETRY_TIME_SECONDS)
        time.sleep(RETRY_TIME_SECONDS)
        tries -= 1
      else:
        raise
