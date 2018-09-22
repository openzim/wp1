from sqlalchemy import Column, Binary
from sqlalchemy.ext.declarative import declarative_base

_Base = declarative_base()

class Release(_Base):
    __tablename__ = 'lucky_releases'

    article = Column('rel_article', Binary(255), primary_key=True)
    category = Column('rel_0p5_category', Binary(63))
    timestamp = Column('rel_0p5_timestamp', Binary(20))

    def __repr__(self):
        return "<Release(value=%r, article=%r, timestamp=%r)>" % (
            self.article, self.category, self.timestamp)
