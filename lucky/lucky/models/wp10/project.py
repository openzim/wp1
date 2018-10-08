from datetime import datetime

from sqlalchemy import Column
from sqlalchemy.dialects.mysql import BINARY, INTEGER

from lucky.constants import TS_FORMAT_WP10
from lucky.wp10_db import Base

class Project(Base):
  __tablename__ = 'lucky_projects'

  project = Column('p_project', BINARY(63), primary_key=True)
  timestamp = Column('p_timestamp', BINARY(14))
  wikipage = Column('p_wikipage', BINARY(255))
  parent = Column('p_parent', BINARY(63))
  shortname = Column('p_shortname', BINARY(255))
  count = Column('p_count', INTEGER(10, unsigned=True))
  qcount = Column('p_qcount', INTEGER(10, unsigned=True))
  icount = Column('p_icount', INTEGER(10, unsigned=True))
  scope = Column('p_scope', INTEGER(10, unsigned=True))
  upload_timestamp = Column('p_upload_timestamp', BINARY(14))

  def __repr__(self):
    return ('<Project(project=%r, timestamp=%r, count=%r, qcount=%r, icount=%r'
            ' scope=%r, wikipage=%r, parent=%r, shortname=%r'
            ' upload_timestamp=%r)>' % (
              self.project, self.timestamp, self.count, self.qcount,
              self.icount, self.scope, self.wikipage, self.parent,
              self.shortname, self.upload_timestamp))

  @property
  def timestamp_dt(self):
    '''The timestamp parsed into a datetime.datetime object.'''
    if self.timestamp is None:
      return datetime(1970, 1, 1)
    return datetime.strptime(self.timestamp.decode('utf-8'), TS_FORMAT_WP10)
