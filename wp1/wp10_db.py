import pymysql.connections
from pymysql.cursors import Cursor

from wp1.db import connect as _connect


def connect() -> pymysql.connections.Connection[Cursor]:
    return _connect("WP10DB")
