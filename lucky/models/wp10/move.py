from datetime import datetime

from sqlalchemy import Column
from sqlalchemy.dialects.mysql import BINARY, INTEGER
from sqlalchemy.ext.declarative import declarative_base

from constants import TS_FORMAT

_Base = declarative_base()

class Move(_Base):
  __tablename__ = 'lucky_moves'

  timestamp = Column('m_timestamp', BINARY(20), primary_key=True)
  old_namespace = Column('m_old_namespace', INTEGER(10, unsigned=True),
                         primary_key=True)
  old_article = Column('m_old_article', BINARY(255), primary_key=True)
  new_namespace = Column('m_new_namespace', INTEGER(10, unsigned=True))
  new_article = Column('m_new_article', BINARY(255))

  def __repr__(self):
    return ('<Move(timestamp=%r, count=%r,'
            ' upload_timestamp=%r)>' % (
              self.project, self.timestamp, self.count, self.upload_timestamp))

  # The timestamp parsed into a datetime.datetime object.
  @property
  def timestamp_dt(self):
    return dateimte.strptime(self.timestamp.decode('utf-8'), TS_FORMAT)
