import attr


@attr.s
class Category:
    table_name = "categories"

    c_project = attr.ib()
    c_type = attr.ib()
    c_rating = attr.ib()
    c_replacement = attr.ib(default=None)
    c_category = attr.ib(default=None)
    c_ranking = attr.ib(default=None)
