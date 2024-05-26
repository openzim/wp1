from functools import partial

from wp1.db import connect


def connect(lang):
  db = f'{lang}wiki_p'
  host = f'{db}.analytics.db.svc.eqiad.wmflabs'
  return connect('WIKIDB', host=replica_host, db=db)
