import pymysql.connections

from wp1.db import connect as _connect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pymysql.cursors import Cursor


def connect() -> "pymysql.connections.Connection[Cursor]":
    return _connect("WP10DB")
