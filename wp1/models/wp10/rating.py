from datetime import datetime
import logging

import attr

from wp1.constants import TS_FORMAT

logger = logging.getLogger(__name__)


@attr.s
class Rating:
  table_name = 'ratings'

  r_project = attr.ib()
  r_namespace = attr.ib()
  r_article = attr.ib()
  r_score = attr.ib(default=0)
  r_quality = attr.ib(default=None)
  r_quality_timestamp = attr.ib(default=None)
  r_importance = attr.ib(default=None)
  r_importance_timestamp = attr.ib(default=None)

  # The timestamp parsed into a datetime.datetime object.
  @property
  def quality_timestamp_dt(self):
    return datetime.strptime(self.r_quality_timestamp.decode('utf-8'),
                             TS_FORMAT)

  @property
  def importance_timestamp_dt(self):
    return datetime.strptime(self.r_importance_timestamp.decode('utf-8'),
                             TS_FORMAT)

  def set_quality_timestamp_dt(self, dt):
    """Sets the quality_timestamp field using a datetime.datetime object"""
    if dt is None:
      logger.warning('Attempt to set rating quality_timestamp to None ignored')
      return
    self.r_quality_timestamp = dt.strftime(TS_FORMAT).encode('utf-8')

  def set_importance_timestamp_dt(self, dt):
    """Sets the quality_timestamp field using a datetime.datetime object"""
    if dt is None:
      logger.warning(
          'Attempt to set rating importance_timestamp to None ignored')
      return
    self.r_importance_timestamp = dt.strftime(TS_FORMAT).encode('utf-8')
