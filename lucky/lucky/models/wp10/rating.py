from datetime import datetime
import logging

from sqlalchemy import Column
from sqlalchemy.dialects.mysql import INTEGER, BINARY

from lucky.constants import TS_FORMAT
from lucky.wp10_db import Base

logger = logging.getLogger(__name__)

class Rating(Base):
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
    return ('<Rating(project=%r, namespace=%r, article=%r, quality=%r,'
            ' quality_timestamp=%r, importance=%r, importance_timestamp=%r,'
            ' score=%r)>' % (
              self.project, self.namespace, self.article, self.quality,
              self.quality_timestamp, self.importance,
              self.importance_timestamp, self.score))

  # The timestamp parsed into a datetime.datetime object.
  @property
  def quality_timestamp_dt(self):
    return datetime.strptime(
      self.quality_timestamp.decode('utf-8'), TS_FORMAT)

  @property
  def importance_timestamp_dt(self):
    return datetime.strptime(
      self.importance_timestamp.decode('utf-8'), TS_FORMAT)

  def set_quality_timestamp_dt(self, dt):
    """Sets the quality_timestamp field using a datetime.datetime object"""
    if dt is None:
      logger.warning('Attempt to set rating quality_timestamp to None ignored')
      return
    self.quality_timestamp = dt.strftime(TS_FORMAT).encode('utf-8')

  def set_importance_timestamp_dt(self, dt):
    """Sets the quality_timestamp field using a datetime.datetime object"""
    if dt is None:
      logger.warning(
        'Attempt to set rating importance_timestamp to None ignored')
      return
    self.importance_timestamp = dt.strftime(TS_FORMAT).encode('utf-8')
