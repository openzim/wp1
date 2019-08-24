import os

import pymysql
import pymysql.cursors

try:
  from wp1.credentials import WP10_CREDS

  def connect():
    kwargs = {
        'charset': None,
        'use_unicode': False,
        'cursorclass': pymysql.cursors.DictCursor,
        **WP10_CREDS
    }
    return pymysql.connect(**kwargs)
except ImportError:
  # No creds, so return an empty connect method that will blow up. This is only
  # to satisfy imports.
  def connect():
    pass
