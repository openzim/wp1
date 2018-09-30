from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

try:
  from lucky.credentials import WP10_DB_STRING
  _engine = create_engine(WP10_DB_STRING)
except ImportError:
  # This won't actually work because the tables are not there
  _engine = create_engine('sqlite:///:memory:')

Base = declarative_base()
Session = sessionmaker(bind=_engine)

