import datetime
import logging
import uuid

import attr

from wp1.constants import TS_FORMAT_WP10
from wp1.timestamp import utcnow

logger = logging.getLogger(__name__)


@attr.s
class Selection:
    table_name = "selections"

    # Contains the builder's UUID v4 as UTF-8 bytes.
    s_builder_id: bytes = attr.ib()
    s_content_type: bytes = attr.ib()
    s_version: int = attr.ib()
    # This is required, but is set by the set_id method below.
    s_id: bytes | None = attr.ib(default=None)
    # This is required, but set after the selection is uploaded to s3-like storage.
    s_object_key: str | bytes | None = attr.ib(default=None)
    s_updated_at: bytes | None = attr.ib(default=None)
    # The data that is stored in the backend s3-like storage. Not saved to the database.
    data: bytes | None = attr.ib(default=None)
    # THis is Assigned as bytes from DB reads, str from application code paths.
    s_status: str | bytes | None = attr.ib(default=None)
    # JSON string from json.dumps when set in app and bytes when read from DB.
    s_error_messages: str | bytes | None = attr.ib(default=None)
    s_article_count: int | None = attr.ib(default=None)

    def set_id(self) -> None:
        self.s_id = str(uuid.uuid4()).encode("utf-8")

    @property
    def updated_at_dt(self) -> datetime.datetime:
        """The timestamp parsed into a datetime.datetime object."""
        if self.s_updated_at is None:
            raise ValueError("s_updated_at is not set")
        return datetime.datetime.strptime(
            self.s_updated_at.decode("utf-8"), TS_FORMAT_WP10
        )

    def set_updated_at_dt(self, dt: datetime.datetime | None) -> None:
        """Sets the updated_at field using a datetime.datetime object"""
        if dt is None:
            logger.warning("Attempt to set selection updated_at to None ignored")
            return
        self.s_updated_at = dt.strftime(TS_FORMAT_WP10).encode("utf-8")

    def set_updated_at_now(self) -> None:
        """Sets the updated_at field to a timestamp that is equal to now"""
        self.set_updated_at_dt(utcnow())
