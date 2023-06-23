import datetime

import attr

from wp1.constants import TS_FORMAT_WP10
from wp1.timestamp import utcnow


@attr.s
class ZimFile:
  table_name = 'zim_files'

  z_id = attr.ib()
  z_selection_id = attr.ib()
  z_status = attr.ib(default=b'NOT_REQUESTED')
  z_task_id = attr.ib(default=None)
  z_requested_at = attr.ib(default=None)
  z_updated_at = attr.ib(default=None)
  z_long_description = attr.ib(default=None)
  z_description = attr.ib(default=None)

  @property
  def updated_at_dt(self):
    """The timestamp parsed into a datetime.datetime object."""
    return datetime.datetime.strptime(self.z_updated_at.decode('utf-8'),
                                      TS_FORMAT_WP10)

  def set_updated_at_dt(self, dt):
    """Sets the updated_at field using a datetime.datetime object"""
    if dt is None:
      logger.warning(
          'Attempt to set selection zim_file_updated_at to None ignored')
      return
    self.z_updated_at = dt.strftime(TS_FORMAT_WP10).encode('utf-8')

  def set_updated_at_now(self):
    """Sets the zim_file_updated_at field to a timestamp that is equal to now"""
    self.set_updated_at_dt(utcnow())
