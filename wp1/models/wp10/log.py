from datetime import datetime

import attr

from wp1.constants import TS_FORMAT, TS_FORMAT_WP10


@attr.s
class Log:
    table_name = "logging"

    l_project = attr.ib()
    l_namespace = attr.ib()
    l_article = attr.ib()
    l_action = attr.ib()
    l_timestamp = attr.ib()
    l_old = attr.ib()
    l_new = attr.ib()
    l_revision_timestamp = attr.ib()

    @property
    def timestamp_dt(self):
        """The timestamp parsed into a datetime.datetime object."""
        return datetime.strptime(self.l_timestamp.decode("utf-8"), TS_FORMAT_WP10)

    @property
    def rev_timestamp_dt(self):
        """The revision timestamp parsed into a datetime.datetime object."""
        return datetime.strptime(self.l_revision_timestamp.decode("utf-8"), TS_FORMAT)
