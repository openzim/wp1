from sqlalchemy import Column, Binary
from sqlalchemy.ext.declarative import declarative_base

_Base = declarative_base()

class Review(_Base):
    __tablename__ = 'reviews'

    value = Column('rev_value', Binary(10))
    article = Column('rev_article', Binary(255), primary_key=True)
    timestamp = Column('rev_timestamp', Binary(20))

    def __repr__(self):
        return "<Review(value=%r, article=%r, timestamp=%r)>" % (
            self.value, self.article, self.timestamp)
