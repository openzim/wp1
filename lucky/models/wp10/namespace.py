import enum

from sqlalchemy import Column, Enum
from sqlalchemy.dialects.mysql import BINARY, INTEGER
from sqlalchemy.ext.declarative import declarative_base

_Base = declarative_base()

class NsType(enum.Enum):
  primary = 0
  canonical = 1
  alias = 2

class Namespace(_Base):
  __tablename__ = 'namespacename'

  dbname = Column('dbname', BINARY(32))
  domain = Column('domain', BINARY(48), primary_key=True)
  id = Column('ns_id', INTEGER(8))
  name = Column('ns_name', BINARY(255), primary_key=True)
  type = Column('ns_type', Enum(NsType), primary_key=True)

  def __repr__(self):
    return ('<NamespaceName(dbname=%r, domain=%r, id=%r, '
            'name=%r, type=%r)>' % (
             self.dbname, self.domain, self.id, self.name, self.type))
