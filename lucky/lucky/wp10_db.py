import os

import pymysql
import pymysql.cursors

try:
  from credentials import WP10_CREDS
except ImportError:
  raise ImportError('Could not find credentials module. Have you populated it '
                    'based on credentials.py.example?')

def connect():
  kwargs = {
    'charset': None,
    'use_unicode': False,
    'cursorclass': pymysql.cursors.DictCursor,
    **WP10_CREDS
  }

  return pymysql.connect(**kwargs)
