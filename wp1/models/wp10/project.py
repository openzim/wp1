from datetime import datetime

import attr

from wp1.constants import TS_FORMAT_WP10


@attr.s
class Project:
    table_name = "projects"

    p_project = attr.ib()
    p_timestamp = attr.ib()
    p_wikipage = attr.ib(default=None)
    p_parent = attr.ib(default=None)
    p_shortname = attr.ib(default=None)
    p_count = attr.ib(default=None)
    p_qcount = attr.ib(default=None)
    p_icount = attr.ib(default=None)
    p_upload_timestamp = attr.ib(default=None)
    p_scope = attr.ib(default=0)

    @property
    def timestamp_dt(self):
        """The timestamp parsed into a datetime.datetime object."""
        if self.p_timestamp is None:
            return datetime(1970, 1, 1)
        return datetime.strptime(self.p_timestamp.decode("utf-8"), TS_FORMAT_WP10)

    def to_web_dict(self):
        return {
            "name": self.p_project.decode("utf-8").replace("_", " "),
            "last_updated": self.p_timestamp.decode("utf-8"),
        }
