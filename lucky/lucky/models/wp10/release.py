from sqlalchemy import Column
from sqlalchemy.dialects.mysql import BINARY

from lucky.wp10_db import Base

class Release(Base):
  __tablename__ = 'lucky_releases'

  article = Column('rel_article', BINARY(255), primary_key=True)
  category = Column('rel_0p5_category', BINARY(63))
  timestamp = Column('rel_0p5_timestamp', BINARY(20))

  def __repr__(self):
    return "<Release(value=%r, article=%r, timestamp=%r)>" % (
      self.article, self.category, self.timestamp)
