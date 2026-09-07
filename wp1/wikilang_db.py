from pymysql import Connection

from pymysql.cursors import Cursor
from wp1.db import connect as db_connect


def connect(lang, **overrides: object) -> Connection[Cursor]:
    wiki = f"{lang}wiki"
    db = f"{wiki}_p"
    host = f"{wiki}.analytics.db.svc.eqiad.wmflabs"
    return db_connect("WIKIDB", host=host, db=db, **overrides)
