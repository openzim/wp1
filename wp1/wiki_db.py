import os

import pymysql
import pymysql.cursors

try:
  from wp1.credentials import WIKI_CREDS

  def connect():
    kwargs = {
        'charset': None,
        'use_unicode': False,
        'cursorclass': pymysql.cursors.SSDictCursor,
        **WIKI_CREDS
    }
    return pymysql.connect(**kwargs)

except ImportError:
  # No creds, so return an empty connect method that will blow up. This is only
  # to satisfy imports.
  def connect():
    pass
