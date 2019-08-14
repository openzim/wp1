import logging
import os

import pymysql
import pymysql.cursors

logger = logging.getLogger(__name__)

def connect():
  try:
    from lucky.credentials import WIKI_CREDS
    kwargs = {
      'charset': None,
      'use_unicode': False,
      'cursorclass': pymysql.cursors.SSDictCursor,
      **WIKI_CREDS
    }
    return pymysql.connect(**kwargs)
  except ImportError:
    # No creds, so return an empty connection. This will likely blow up any
    # methods that require a connection.
    logger.error('No db credentials found. Have you created credentials.py?')
    return None

connection = connect()
