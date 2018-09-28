from datetime import datetime

from sqlalchemy import Column
from sqlalchemy.dialects.mysql import INTEGER, BINARY
from sqlalchemy.ext.declarative import declarative_base

_Base = declarative_base()

TABLE_TS_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

class Rating(_Base):
  __tablename__ = 'lucky_ratings'

  project = Column('r_project', BINARY(63), primary_key=True)
  namespace = Column('r_namespace',
                     INTEGER(10, unsigned=True), primary_key=True)
  article = Column('r_article', BINARY(255), primary_key=True)
  quality = Column('r_quality', BINARY(63))
  quality_timestamp = Column('r_quality_timestamp', BINARY(20))
  importance = Column('r_importance', BINARY(63))
  importance_timestamp = Column('r_importance_timestamp', BINARY(20))
  score = Column('r_score', INTEGER(8, unsigned=True))

  def __repr__(self):
    return ('<Rating(project=%r, timestamp=%r, count=%r,'
            ' upload_timestamp=%r)>' % (
              self.project, self.timestamp, self.count, self.upload_timestamp))

  # The timestamp parsed into a datetime.datetime object.
  @property
  def quality_timestamp_dt(self):
    return datetime.strptime(
      self.quality_timestamp.decode('utf-8'), TABLE_TS_FORMAT)

  @property
  def importance_timestamp_dt(self):
    return datetime.strptime(
      self.importance_timestamp.decode('utf-8'), TABLE_TS_FORMAT)

  def set_quality_timestamp_dt(self, dt):
    """Sets the quality_timestamp field using a datetime.datetime object"""
    self.quality_timestamp = dt.strftime(TABLE_TS_FORMAT).encode('utf-8')

  def set_importance_timestamp_dt(self, dt):
    """Sets the quality_timestamp field using a datetime.datetime object"""
    self.importance_timestamp = dt.strftime(TABLE_TS_FORMAT).encode('utf-8')
