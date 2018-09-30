import datetime

from sqlalchemy import Column
from sqlalchemy.dialects.mysql import BIGINT, BINARY, BLOB, INTEGER
from sqlalchemy.ext.declarative import declarative_base

from lucky.wiki_db import Base

class Log(Base):
  __tablename__ = 'logging'

  id = Column('log_id', INTEGER(10, unsigned=True), primary_key=True)
  namespace = Column('log_namespace', BIGINT(11))
  type = Column('log_type', BINARY(32))
  title = Column('log_title', BINARY(255))
  timestamp = Column('log_timestamp', BINARY(14))
  params = Column('log_params', BLOB)

  def __repr__(self):
    return "<Log(namespace=%r, title=%r, timestamp=%r, type=%r)>" % (
      self.namespace, self.title, self.timestamp, self.type)

  @property
  def timestamp_dt(self):
    return datetime.strptime(
      self.quality_timestamp.decode('utf-8'), '%Y%m%dT%H%M%S')
