import attr


@attr.s
class Release:
    table_name = "releases"

    rel_article: bytes = attr.ib()
    rel_0p5_category: bytes = attr.ib()
    rel_0p5_timestamp: bytes = attr.ib()
