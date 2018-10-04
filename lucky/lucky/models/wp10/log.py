from datetime import datetime

from sqlalchemy import Column
from sqlalchemy.dialects.mysql import BINARY, INTEGER

from lucky.constants import TS_FORMAT
from lucky.wp10_db import Base

class Log(Base):
  __tablename__ = 'lucky_logging'

  project = Column('p_project', BINARY(63), primary_key=True)
  namespace = Column(
    'l_namespace', INTEGER(10, unsigned=True), primary_key=True)
  article = Column('l_article', BINARY(255), primary_key=True)
  action = Column('l_action', BINARY(20), primary_key=True)
  timestamp = Column('l_timestamp', BINARY(14), primary_key=True)
  old = Column('l_old', BINARY(63))
  new = Column('l_new', BINARY(63))
  revision_timestamp = Column('l_revision_timestamp', BINARY(20))

  def __repr__(self):
    return ('<Log(project=%r, namespace=%r, article=%r, action=%r, '
            'timestamp=%r, old=%r, new=%r, revision_timestamp=%r)>' % (
            self.project, self.namespace, self.article, self.action,
            self.timestamp, self.old, self.new, self.revision_timestamp))

  # The timestamp parsed into a datetime.datetime object.
  @property
  def timestamp_dt(self):
    return datetime.strptime(self.timestamp.decode('utf-8'), TS_FORMAT)
