import enum
from typing import Optional
import attr


class NsType(enum.Enum):
    primary = 0
    canonical = 1
    alias = 2


@attr.s
class Namespace:
    table_name = "namespacename"

    domain: bytes = attr.ib()
    ns_name: bytes = attr.ib()
    ns_type: NsType = attr.ib()
    ns_id: Optional[int] = attr.ib(default=None)
    dbname: Optional[bytes] = attr.ib(default=None)
