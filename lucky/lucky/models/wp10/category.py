from sqlalchemy import Column
from sqlalchemy.dialects.mysql import BINARY, INTEGER
from sqlalchemy.ext.declarative import declarative_base

_Base = declarative_base()

class Category(_Base):
  __tablename__ = 'lucky_categories'

  project = Column('c_project', BINARY(63), primary_key=True)
  type = Column('c_type', BINARY(16), primary_key=True)
  rating = Column('c_rating', BINARY(63), primary_key=True)
  replacement = Column('c_replacement', BINARY(63))
  category = Column('c_category', BINARY(255))
  ranking = Column('c_ranking', INTEGER(10, unsigned=True))

  def __repr__(self):
    return ('<Category(project=%r, type=%r, rating=%r, replacement=%r',
            ' category=%r, ranking=%r)>' % (
              self.project, self.type, self.rating, self.replacement,
              self.category, self.ranking))
