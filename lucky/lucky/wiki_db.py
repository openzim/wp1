import os

import pymysql
import pymysql.cursors

def connect():
  return pymysql.connect(
    db='enwiki_p',
    host="enwiki.analytics.db.svc.eqiad.wmflabs",
    read_default_file=os.path.expanduser("~/replica.my.cnf"),
    charset=None,
    use_unicode=False,
    cursorclass=pymysql.cursors.SSDictCursor)
