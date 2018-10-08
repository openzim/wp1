from sqlalchemy import Column
from sqlalchemy.dialects.mysql import INTEGER, BINARY

from lucky.wp10_db import Base

class SelectionData(Base):
  __tablename__ = 'selection_data'

  article = Column('sd_article', BINARY(255), primary_key=True)
  langlinks = Column('sd_langlinks', INTEGER(10, unsigned=True))
  pagelinks = Column('sd_pagelinks', INTEGER(10, unsigned=True))
  hitcount = Column('sd_hitcount', INTEGER(10, unsigned=True))
  external = Column('sd_external', INTEGER(10, unsigned=True))

  def __repr__(self):
    return ('<SelectionData(article=%r, langlinks=%r, pagelinks=%r,'
            ' hitcount=%r, external=%r)>' % (
              self.article, self.langlinks, self.pagelinks, self.hitcount,
              self.external))
