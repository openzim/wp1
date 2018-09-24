from datetime import datetime

from sqlalchemy import Column, Binary
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.ext.declarative import declarative_base

_Base = declarative_base()

class Project(_Base):
  __tablename__ = 'lucky_projects'

  project = Column('p_project', Binary(63), primary_key=True)
  timestamp = Column('p_timestamp', Binary(14))
  count = Column('p_count', INTEGER(10, unsigned=True))
  upload_timestamp = Column('p_upload_timestamp', Binary(14))

  def __repr__(self):
    return ('<Project(project=%r, timestamp=%r, count=%r,'
            ' upload_timestamp=%r)>' % (
              self.project, self.timestamp, self.count, self.upload_timestamp))

  # The timestamp parsed into a datetime.datetime object.
  @property
  def timestamp_dt(self):
    return dateimte.strptime(
      self.timestamp.decode('utf-8'), '%Y-%m-%dT%H:%M:%SZ')
