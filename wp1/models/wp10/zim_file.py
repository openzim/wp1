import datetime
import logging

import attr

from wp1.constants import TS_FORMAT_WP10
from wp1.timestamp import utcnow

logger = logging.getLogger(__name__)


@attr.s
class ZimTask:
    table_name = "zim_tasks"

    z_id: int = attr.ib()
    # Contains a Selection UUID v4 as UTF-8 bytes.
    z_selection_id: bytes = attr.ib()
    z_status: bytes = attr.ib(default=b"NOT_REQUESTED")
    z_task_id: bytes | None = attr.ib(default=None)
    z_requested_at: bytes | None = attr.ib(default=None)
    z_updated_at: bytes | None = attr.ib(default=None)
    # Contains a ZimSchedule UUID v4 as UTF-8 bytes.
    z_zim_schedule_id: bytes | None = attr.ib(default=None)

    @property
    def updated_at_dt(self) -> datetime.datetime:
        """The timestamp parsed into a datetime.datetime object."""
        if self.z_updated_at is None:
            raise ValueError("z_updated_at is not set")
        return datetime.datetime.strptime(
            self.z_updated_at.decode("utf-8"), TS_FORMAT_WP10
        )

    def set_updated_at_dt(self, dt: datetime.datetime | None) -> None:
        """Sets the updated_at field using a datetime.datetime object"""
        if dt is None:
            logger.warning(
                "Attempt to set selection zim_file_updated_at to None ignored"
            )
            return
        self.z_updated_at = dt.strftime(TS_FORMAT_WP10).encode("utf-8")

    def set_updated_at_now(self) -> None:
        """Sets the zim_file_updated_at field to a timestamp that is equal to now"""
        self.set_updated_at_dt(utcnow())
