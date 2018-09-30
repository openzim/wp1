import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lucky.wp10_db import Base as WpOneBase
from lucky.wiki_db import Base as WikiBase

class _OrmTest(unittest.TestCase):
  engine = create_engine('sqlite:///:memory:')
  Session = sessionmaker(bind=engine)
  session = Session()

  def setUp(self):
    self.Base.metadata.create_all(self.engine)

  def tearDown(self):
    self.Base.metadata.drop_all(self.engine)

class BaseWpOneOrmTest(unittest.TestCase):
  Base = WpOneBase

class BaseWikiOrmTest(unittest.TestCase):
  Base = WikiBase
