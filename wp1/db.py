import logging
import os
import time

import pymysql
import pymysql.cursors
import pymysql.err
import socks

logger = logging.getLogger(__name__)

try:
  from wp1.credentials import CREDENTIALS, ENV
except ImportError:
  logger.exception('The file credentials.py must be populated manually in '
                   'order to connect to the required databases')
  CREDENTIALS = None
  ENV = None

RETRY_TIME_SECONDS = 5


def connect(db_name, **overrides):
  creds = CREDENTIALS[ENV].get(db_name)
  if creds is None:
    raise ValueError('db credentials for %r in ENV=%s are None' %
                     (db_name, ENV))

  kwargs = {
      'charset': None,
      'use_unicode': False,
      'cursorclass': pymysql.cursors.SSDictCursor,
      **creds,
      **overrides
  }

  tries = 4
  while True:
    try:
      if db_name == 'WIKIDB' and ENV == ENV.DEVELOPMENT:
        # In development, connect through a SOCKS5 proxy so that hosts on
        # *.eqiad.wmflabs can be reached.
        s = socks.socksocket()
        s.set_proxy(socks.SOCKS5, 'localhost')
        s.connect((kwargs['host'], kwargs.get('port', 3306)))
        conn = pymysql.connect(**kwargs, defer_connect=True)
        conn.connect(sock=s)
      else:
        conn = pymysql.connect(**kwargs)

      return conn
    except pymysql.err.InternalError:
      if tries > 0:
        logging.warning('Could not connect to database, retrying in %s seconds',
                        RETRY_TIME_SECONDS)
        time.sleep(RETRY_TIME_SECONDS)
        tries -= 1
      else:
        raise
