import datetime
import logging
import uuid

import attr

from wp1.constants import TS_FORMAT_WP10
from wp1.timestamp import utcnow

logger = logging.getLogger(__name__)


@attr.s
class Selection:
  table_name = 'selections'

  s_builder_id = attr.ib()
  s_content_type = attr.ib()
  s_version = attr.ib()
  # This is required, but is set by the set_id method below.
  s_id = attr.ib(default=None)
  # This is required, but set after the selection is uploaded to s3-like storage.
  s_object_key = attr.ib(default=None)
  s_updated_at = attr.ib(default=None)
  # The data that is stored in the backend s3-like storage. Not saved to the database.
  data = attr.ib(default=None)
  s_status = attr.ib(default=None)
  s_error_messages = attr.ib(default=None)

  def set_id(self):
    self.s_id = str(uuid.uuid4()).encode('utf-8')

  @property
  def updated_at_dt(self):
    """The timestamp parsed into a datetime.datetime object."""
    return datetime.datetime.strptime(self.s_updated_at.decode('utf-8'),
                                      TS_FORMAT_WP10)

  def set_updated_at_dt(self, dt):
    """Sets the updated_at field using a datetime.datetime object"""
    if dt is None:
      logger.warning('Attempt to set selection updated_at to None ignored')
      return
    self.s_updated_at = dt.strftime(TS_FORMAT_WP10).encode('utf-8')

  def set_updated_at_now(self):
    """Sets the updated_at field to a timestamp that is equal to now"""
    self.set_updated_at_dt(utcnow())
