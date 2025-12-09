import attr


@attr.s
class Release:
    table_name = "releases"

    rel_article = attr.ib()
    rel_0p5_category = attr.ib()
    rel_0p5_timestamp = attr.ib()
