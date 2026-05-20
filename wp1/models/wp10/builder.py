import datetime
import json
import logging
import uuid
from typing import Any

import attr

from wp1.constants import TS_FORMAT_WP10
from wp1.timestamp import utcnow

logger = logging.getLogger(__name__)


def builder_id() -> bytes:
    return str(uuid.uuid4()).encode("utf-8")


@attr.s
class Builder:
    table_name = "builders"

    b_name: bytes = attr.ib()
    b_user_id: bytes = attr.ib()
    b_project: bytes = attr.ib()
    b_model: bytes = attr.ib()
    b_params: bytes = attr.ib()
    # Needs to be set before insertion into the database
    # contains a UUID v4 string encoded as UTF-8 bytes.
    b_id: bytes | None = attr.ib(default=None)
    b_created_at: bytes | None = attr.ib(default=None)
    b_updated_at: bytes | None = attr.ib(default=None)
    b_current_version: int = attr.ib(default=0)
    b_selection_zim_version: int = attr.ib(default=0)

    @property
    def created_at_dt(self) -> datetime.datetime:
        """The timestamp parsed into a datetime.datetime object."""
        if self.b_created_at is None:
            raise ValueError("b_created_at is not set")
        return datetime.datetime.strptime(
            self.b_created_at.decode("utf-8"), TS_FORMAT_WP10
        )

    def set_created_at_dt(self, dt: datetime.datetime | None) -> None:
        """Sets the created_at field using a datetime.datetime object"""
        if dt is None:
            logger.warning("Attempt to set selection created_at to None ignored")
            return
        self.b_created_at = dt.strftime(TS_FORMAT_WP10).encode("utf-8")

    def set_created_at_now(self) -> None:
        """Sets the created_at field to a timestamp that is equal to now"""
        self.set_created_at_dt(utcnow())

    @property
    def updated_at_dt(self) -> datetime.datetime:
        """The timestamp parsed into a datetime.datetime object."""
        if self.b_updated_at is None:
            raise ValueError("b_updated_at is not set")
        return datetime.datetime.strptime(
            self.b_updated_at.decode("utf-8"), TS_FORMAT_WP10
        )

    def set_updated_at_dt(self, dt: datetime.datetime | None) -> None:
        """Sets the updated_at field using a datetime.datetime object"""
        if dt is None:
            logger.warning("Attempt to set selection updated_at to None ignored")
            return
        self.b_updated_at = dt.strftime(TS_FORMAT_WP10).encode("utf-8")

    def set_updated_at_now(self) -> None:
        """Sets the updated_at field to a timestamp that is equal to now"""
        self.set_updated_at_dt(utcnow())

    def to_web_dict(self) -> dict[str, Any]:
        return {
            "name": self.b_name.decode("utf-8"),
            "project": self.b_project.decode("utf-8"),
            "params": json.loads(self.b_params.decode("utf-8")),
            "model": self.b_model.decode("utf-8"),
        }

    def set_id(self) -> None:
        self.b_id = builder_id()
