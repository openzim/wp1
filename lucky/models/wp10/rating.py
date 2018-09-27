from datetime import datetime

from sqlalchemy import Column, Binary
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.ext.declarative import declarative_base

_Base = declarative_base()

class Rating(_Base):
  __tablename__ = 'lucky_ratings'

  project = Column('r_project', Binary(63), primary_key=True)
  namespace = Column('r_namespace',
                     INTEGER(10, unsigned=True), primary_key=True)
  article = Column('r_article', Binary(255), primary_key=True)
  quality = Column('r_quality', Binary(63))
  quality_timestamp = Column('r_quality_timestamp', Binary(20))
  importance = Column('r_importance', Binary(63))
  importance_timestamp = Column('r_importance_timestamp', Binary(20))
  score = Column('r_score', INTEGER(8, unsigned=True))

  def __repr__(self):
    return ('<Rating(project=%r, timestamp=%r, count=%r,'
            ' upload_timestamp=%r)>' % (
              self.project, self.timestamp, self.count, self.upload_timestamp))

  # The timestamp parsed into a datetime.datetime object.
  @property
  def quality_timestamp_dt(self):
    return dateimte.strptime(
      self.quality_timestamp.decode('utf-8'), '%Y-%m-%dT%H:%M:%SZ')

  @property
  def importance_timestamp_dt(self):
    return dateimte.strptime(
      self.importance_timestamp.decode('utf-8'), '%Y-%m-%dT%H:%M:%SZ')
