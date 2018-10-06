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

class BaseWpOneOrmTest(_OrmTest):
  Base = WpOneBase

class BaseWikiOrmTest(_OrmTest):
  Base = WikiBase

class BaseCombinedOrmTest(unittest.TestCase):
  wiki_engine = create_engine('sqlite:///:memory:')
  WikiSession = sessionmaker(bind=wiki_engine)
  wiki_session = WikiSession()

  wp10_engine = create_engine('sqlite:///:memory:')
  Wp10Session = sessionmaker(bind=wp10_engine)
  wp10_session = Wp10Session()

  def setUp(self):
    WpOneBase.metadata.create_all(self.wp10_engine)
    WikiBase.metadata.create_all(self.wiki_engine)

  def tearDown(self):
    WpOneBase.metadata.drop_all(self.wp10_engine)
    WikiBase.metadata.drop_all(self.wiki_engine)
