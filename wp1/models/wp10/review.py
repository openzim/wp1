from sqlalchemy import Column
from sqlalchemy.dialects.mysql import BINARY

from wp1.wp10_db import Base


class Review(Base):
    __tablename__ = "reviews"

    value = Column("rev_value", BINARY(10))
    article = Column("rev_article", BINARY(255), primary_key=True)
    timestamp = Column("rev_timestamp", BINARY(20))

    def __repr__(self):
        return "<Review(value=%r, article=%r, timestamp=%r)>" % (
            self.value,
            self.article,
            self.timestamp,
        )
