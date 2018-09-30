import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lucky.wp10_db import Base as WpOneBase

class BaseWpOneOrmTest(unittest.TestCase):
  engine = create_engine('sqlite:///:memory:')
  Session = sessionmaker(bind=engine)
  session = Session()

  def setUp(self):
    WpOneBase.metadata.create_all(self.engine)

  def tearDown(self):
    WpOneBase.metadata.drop_all(self.engine)
