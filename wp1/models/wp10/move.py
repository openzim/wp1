from datetime import datetime

import attr

from wp1.constants import TS_FORMAT


@attr.s
class Move:
    table_name = "moves"

    m_timestamp = attr.ib()
    m_old_namespace = attr.ib()
    m_old_article = attr.ib()
    m_new_namespace = attr.ib(default=None)
    m_new_article = attr.ib(default=None)

    # The timestamp parsed into a datetime.datetime object.
    @property
    def timestamp_dt(self):
        return datetime.strptime(self.timestamp.decode("utf-8"), TS_FORMAT)
