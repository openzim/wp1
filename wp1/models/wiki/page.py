import attr

from wp1.conf import get_conf

config = get_conf()
ARTICLES_LABEL_STR = config["ARTICLES_LABEL"]
BY_QUALITY_STR = config["BY_QUALITY"]


@attr.s
class Page:
    """An approximation of a wikipedia page, for use in this bot.

    This class simultaneously is missing fields from the page table, and includes
    other fields from the categorylinks table. It is produced primarily by the
    wp1.logic.page method get_pages_by_category.
    """

    table_name = "page"

    page_id = attr.ib()
    page_namespace = attr.ib()
    page_title = attr.ib()
    cl_sortkey = attr.ib(default=None)
    cl_timestamp = attr.ib(default=None)

    @property
    def base_title(self):
        bytes_to_replace = ("_%s_%s" % (ARTICLES_LABEL_STR, BY_QUALITY_STR)).encode(
            "utf-8"
        )
        return self.page_title.replace(bytes_to_replace, b"")
