import enum

import attr


class NsType(enum.Enum):
    primary = 0
    canonical = 1
    alias = 2


@attr.s
class Namespace:
    table_name = "namespacename"

    domain = attr.ib()
    ns_name = attr.ib()
    ns_type = attr.ib()
    ns_id = attr.ib(default=None)
    dbname = attr.ib(default=None)
