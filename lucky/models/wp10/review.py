from sqlalchemy import Column
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy.ext.declarative import declarative_base

_Base = declarative_base()

class Review(_Base):
  __tablename__ = 'lucky_reviews'

  value = Column('rev_value', BINARY(10))
  article = Column('rev_article', BINARY(255), primary_key=True)
  timestamp = Column('rev_timestamp', BINARY(20))

  def __repr__(self):
    return "<Review(value=%r, article=%r, timestamp=%r)>" % (
      self.value, self.article, self.timestamp)
