from pymysql import Connection
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pymysql.cursors import Cursor
from wp1.db import connect as db_connect


def db_lang_prefix(lang: str) -> str:
    prefix = lang.replace("-", "_")
    if prefix == "be_tarask":
        return "be_x_old"
    return prefix


def connect(lang, **overrides: object) -> "Connection[Cursor]":
    prefix = db_lang_prefix(lang)
    wiki = f"{prefix}wiki"
    db = f"{wiki}_p"
    host = f"{wiki}.analytics.db.svc.eqiad.wmflabs"
    return db_connect("WIKIDB", host=host, db=db, **overrides)
