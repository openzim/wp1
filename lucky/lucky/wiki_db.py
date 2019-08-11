import os

import pymysql
import pymysql.cursors

try:
  from credentials import WIKI_CREDS
except ImportError:
  raise ImportError('Could not find credentials module. Have you populated it '
                    'based on credentials.py.example?')

def connect():
  kwargs = {
    'charset': None,
    'use_unicode': False,
    'cursorclass': pymysql.cursors.SSDictCursor,
    **WIKI_CREDS
  }

  return pymysql.connect(**kwargs)
