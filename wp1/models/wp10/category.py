import attr
from typing import Optional


@attr.s
class Category:
    table_name = "categories"

    c_project: bytes = attr.ib()
    c_type: bytes = attr.ib()
    c_rating: bytes = attr.ib()
    c_replacement: Optional[bytes] = attr.ib(default=None)
    c_category: Optional[bytes] = attr.ib(default=None)
    c_ranking: Optional[int] = attr.ib(default=None)
