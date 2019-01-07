import os

import pymysql
import pymysql.cursors

conn = pymysql.connect(
  host='tools.db.svc.eqiad.wmflabs',
  db='s51114_enwp10',
  read_default_file=os.path.expanduser('~/replica.my.cnf'),
  charset=None,
  use_unicode=False,
  cursorclass=pymysql.cursors.DictCursor)
