from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

try:
  from lucky.credentials import WIKI_DB_STRING
  _engine = create_engine(WIKI_DB_STRING)
except ImportError:
  # This won't actually work because the tables are not there
  _engine = create_engine('sqlite:///:memory:')

metadata = MetaData()
Base = declarative_base(metadata=metadata)
Session = sessionmaker(bind=_engine)
