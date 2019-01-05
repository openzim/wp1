import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lucky.wp10_db import Base as WpOneBase
from lucky.wiki_db import Base as WikiBase

class _OrmTest(unittest.TestCase):
  def setUp(self):
    self.engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=self.engine)
    self.session = Session()

    self.Base.metadata.create_all(self.engine)

  def tearDown(self):
    self.Base.metadata.drop_all(self.engine)

class BaseWpOneOrmTest(_OrmTest):
  Base = WpOneBase

class BaseWikiOrmTest(_OrmTest):
  Base = WikiBase

class BaseCombinedOrmTest(unittest.TestCase):
  def setUp(self):
    self.wiki_engine = create_engine('sqlite:///:memory:')
    self.WikiSession = sessionmaker(bind=self.wiki_engine)
    self.wiki_session = self.WikiSession()

    self.wp10_engine = create_engine('sqlite:///:memory:')
    self.Wp10Session = sessionmaker(bind=self.wp10_engine)
    self.wp10_session = self.Wp10Session()

    WpOneBase.metadata.create_all(self.wp10_engine)
    WikiBase.metadata.create_all(self.wiki_engine)

  def tearDown(self):
    WpOneBase.metadata.drop_all(self.wp10_engine)
    WikiBase.metadata.drop_all(self.wiki_engine)
    self.wiki_session.close()
    self.wp10_session.close()
    self.wiki_engine.dispose()
    self.wp10_engine.dispose()
