from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.query import Query

class PrefixedQuery(Query):
  '''Used for adding /* SLOW_OK */ prefixes to some queries.'''

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._prefixes = []

  def prefix_with(self, prefix):
    self._prefixes.append(prefix)
    return self

  def _compile_context(self, **kw):
    ctx = super()._compile_context(**kw)
    for prefix in self._prefixes:
      ctx.statement = ctx.statement.prefix_with(prefix)
    return ctx


try:
  from lucky.credentials import WIKI_DB_STRING
  _engine = create_engine(WIKI_DB_STRING, pool_pre_ping=True)
except ImportError:
  # This won't actually work because the tables are not there
  _engine = create_engine('sqlite:///:memory:')

metadata = MetaData()
Base = declarative_base(metadata=metadata)
Session = sessionmaker(bind=_engine, query_cls=PrefixedQuery)
