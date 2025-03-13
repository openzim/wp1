import datetime
import json
import logging
import uuid

import attr

from wp1.constants import TS_FORMAT_WP10
from wp1.timestamp import utcnow

logger = logging.getLogger(__name__)


def builder_id():
  return str(uuid.uuid4()).encode('utf-8')


@attr.s
class Builder:
  table_name = 'builders'

  b_name = attr.ib()
  b_user_id = attr.ib()
  b_project = attr.ib()
  b_model = attr.ib()
  b_params = attr.ib()
  # Needs to be set before insertion into the database
  b_id = attr.ib(default=None)
  b_created_at = attr.ib(default=None)
  b_updated_at = attr.ib(default=None)
  b_current_version = attr.ib(default=0)
  b_selection_zim_version = attr.ib(default=0)

  @property
  def created_at_dt(self):
    """The timestamp parsed into a datetime.datetime object."""
    return datetime.datetime.strptime(self.b_created_at.decode('utf-8'),
                                      TS_FORMAT_WP10)

  def set_created_at_dt(self, dt):
    """Sets the created_at field using a datetime.datetime object"""
    if dt is None:
      logger.warning('Attempt to set selection created_at to None ignored')
      return
    self.b_created_at = dt.strftime(TS_FORMAT_WP10).encode('utf-8')

  def set_created_at_now(self):
    """Sets the created_at field to a timestamp that is equal to now"""
    self.set_created_at_dt(utcnow())

  @property
  def updated_at_dt(self):
    """The timestamp parsed into a datetime.datetime object."""
    return datetime.datetime.strptime(self.b_updated_at.decode('utf-8'),
                                      TS_FORMAT_WP10)

  def set_updated_at_dt(self, dt):
    """Sets the updated_at field using a datetime.datetime object"""
    if dt is None:
      logger.warning('Attempt to set selection updated_at to None ignored')
      return
    self.b_updated_at = dt.strftime(TS_FORMAT_WP10).encode('utf-8')

  def set_updated_at_now(self):
    """Sets the updated_at field to a timestamp that is equal to now"""
    self.set_updated_at_dt(utcnow())

  def to_web_dict(self):
    return {
        'name': self.b_name.decode('utf-8'),
        'project': self.b_project.decode('utf-8'),
        'params': json.loads(self.b_params.decode('utf-8')),
        'model': self.b_model.decode('utf-8'),
    }

  def set_id(self):
    self.b_id = builder_id()
