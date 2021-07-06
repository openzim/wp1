import datetime
import hashlib
import logging

import attr

from wp1.constants import TS_FORMAT_WP10
from wp1.timestamp import utcnow

logger = logging.getLogger(__name__)

try:
  from wp1.credentials import ENV, CREDENTIALS
  SECRET_OBJECT_SALT = CREDENTIALS.get(ENV, {}).get('SECRET_OBJECT_SALT')
except ImportError:
  logger.warning(
      'The file credentials.py must be populated manually and contain '
      'the SECRET_OBJECT_SALT')
  SECRET_OBJECT_SALT = ''


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
  s_created_at = attr.ib(default=None)
  data = attr.ib(default=None)

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

  def calculate_from_id(self, id_):
    """Sets the s_id and the derived s_hash and s_object_key for this selection."""
    if id_ is None:
      raise ValueError('Cannot calculate Selection values with None id')
    if self.s_user_id is None:
      raise ValueError('Cannot calculate Selection values if s_user_id is None')

    self.s_id = id_
    self.s_hash = hashlib.md5(
        ('%s%s' %
         (SECRET_OBJECT_SALT, id_)).encode('utf-8')).hexdigest().encode('utf-8')
    self.s_object_key = b'selections/%s/%s/%s.tsv' % (
        self.s_model, str(self.s_user_id).encode('utf-8'), self.s_hash)
