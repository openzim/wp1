from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from credentials import CREDENTIALED_DB_STRING

_engine = create_engine(CREDENTIALED_DB_STRING)
Session = sessionmaker(bind=_engine)
