from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lucky.credentials import WP10_DB_STRING

_engine = create_engine(WP10_DB_STRING)
Session = sessionmaker(bind=_engine)
