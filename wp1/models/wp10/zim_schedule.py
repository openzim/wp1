import datetime
import logging
import uuid

import attr

from wp1.constants import TS_FORMAT_WP10
from wp1.timestamp import utcnow

logger = logging.getLogger(__name__)


@attr.s
class ZimSchedule:
  table_name = 'zim_schedules'

  s_id: bytes = attr.ib()
  s_builder_id: bytes = attr.ib()
  s_rq_job_id: bytes = attr.ib()
  s_last_updated_at: bytes = attr.ib()
  s_zim_file_id: int = attr.ib(default=None)
  s_interval: int = attr.ib(default=None)  # in months
  s_email: bytes = attr.ib(default=None)  # Email to notify when the zim generation is done
  s_remaining_generations: int = attr.ib(default=None)  # how many more ZIMs to generate

  def set_id(self):
    self.s_id = str(uuid.uuid4()).encode('utf-8')

  @property
  def last_updated_at_dt(self):
    """The timestamp parsed into a datetime.datetime object."""
    return datetime.datetime.strptime(self.s_last_updated_at.decode('utf-8'),
                                      TS_FORMAT_WP10)

  def set_last_updated_at_dt(self, dt):
    """Sets the last_updated_at field using a datetime.datetime object"""
    if dt is None:
      logger.warning('Attempt to set zim schedule last_updated_at to None ignored')
      return
    self.s_last_updated_at = dt.strftime(TS_FORMAT_WP10).encode('utf-8')

  def set_last_updated_at_now(self):
    """Sets the last_updated_at field to a timestamp that is equal to now"""
    self.set_last_updated_at_dt(utcnow())
