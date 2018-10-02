from datetime import datetime

from sqlalchemy import Column
from sqlalchemy.dialects.mysql import BINARY, INTEGER

from lucky.constants import TS_FORMAT
from lucky.wp10_db import Base

class Move(Base):
  __tablename__ = 'lucky_moves'

  timestamp = Column('m_timestamp', BINARY(20), primary_key=True)
  old_namespace = Column('m_old_namespace', INTEGER(10, unsigned=True),
                         primary_key=True)
  old_article = Column('m_old_article', BINARY(255), primary_key=True)
  new_namespace = Column('m_new_namespace', INTEGER(10, unsigned=True))
  new_article = Column('m_new_article', BINARY(255))

  def __repr__(self):
    return ('<Move(timestamp=%r, old_namespace=%r, old_article=%r,'
            ' new_namespace=%r, new_article=%r)>' % (
              self.timestamp, self.old_namespace, self.old_article,
              self.new_namespace, self.new_article))

  # The timestamp parsed into a datetime.datetime object.
  @property
  def timestamp_dt(self):
    return datetime.strptime(self.timestamp.decode('utf-8'), TS_FORMAT)
