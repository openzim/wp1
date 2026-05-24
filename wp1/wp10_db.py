import pymysql.connections

from wp1.db import connect as _connect


def connect() -> pymysql.connections.Connection:
    return _connect("WP10DB")
