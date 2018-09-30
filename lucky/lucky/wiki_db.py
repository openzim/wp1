from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lucky.credentials import WIKI_DB_STRING

_engine = create_engine(WIKI_DB_STRING)
Session = sessionmaker(bind=_engine)
