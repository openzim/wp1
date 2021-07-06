import datetime

import attr

from wp1.constants import TS_FORMAT_WP10
from wp1.timestamp import utcnow


@attr.s
class Selection:
  table_name = 'selections'

  s_name = attr.ib()
  s_user_id = attr.ib()
  s_project = attr.ib()
  s_id = attr.ib(default=None)
  s_hash = attr.ib(default=None)
  s_model = attr.ib(default=None)
  s_region = attr.ib(default=None)
  s_bucket = attr.ib(default=None)
  s_object_key = attr.ib(default=None)
  s_last_generated = attr.ib(default=None)

  # The timestamp parsed into a datetime.datetime object.
  @property
  def last_generated_dt(self):
    return datetime.datetime.strptime(self.s_last_generated.decode('utf-8'),
                                      TS_FORMAT_WP10)

  def set_last_generated_dt(self, dt):
    """Sets the last_generated field using a datetime.datetime object"""
    if dt is None:
      logger.warning('Attempt to set selection last_generated to None ignored')
      return
    self.s_last_generated = dt.strftime(TS_FORMAT_WP10).encode('utf-8')

  def set_last_generated_now(self):
    """Sets the last_generated field to a timestamp that is equal to now"""
    self.set_last_generated_dt(utcnow())

  # The timestamp parsed into a datetime.datetime object.
  @property
  def created_at_dt(self):
    return datetime.datetime.strptime(self.s_created_at.decode('utf-8'),
                                      TS_FORMAT_WP10)

  def set_created_at_dt(self, dt):
    """Sets the created_at field using a datetime.datetime object"""
    if dt is None:
      logger.warning('Attempt to set selection created_at to None ignored')
      return
    self.s_created_at = dt.strftime(TS_FORMAT_WP10).encode('utf-8')

  def set_created_at_now(self):
    """Sets the created_at field to a timestamp that is equal to now"""
    self.set_created_at_dt(utcnow())
