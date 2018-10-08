from sqlalchemy import Column
from sqlalchemy.dialects.mysql import INTEGER, BINARY

from lucky.wp10_db import Base

class GlobalRanking(Base):
  __tablename__ = 'global_rankings'

  type = Column('gr_type', BINARY(16), primary_key=True)
  rating = Column('gr_rating', BINARY(63), primary_key=True)
  ranking = Column('gr_ranking', INTEGER(10, unsigned=True))

  def __repr__(self):
    return ('<GlobalRanking(type=%r, rating=%r, ranking=%r)>' % (
            self.type, self.rating, self.ranking))
