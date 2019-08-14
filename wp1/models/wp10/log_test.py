from wp1.base_db_test import BaseWpOneDbTest
from wp1.logic import log as logic_log
from wp1.models.wp10.log import Log

class ModelsLogTest(BaseWpOneDbTest):
  def setUp(self):
    super().setUp()
    self.project_name = b'My test project'
    self.ns = 0
    self.article = b'The Art of Testing (book)'
    self.action = b'quality'
    self.timestamp = b'20180401123000'
    self.log = Log(
      l_project=self.project_name, l_namespace=self.ns, l_article=self.article,
      l_action=self.action, l_timestamp=self.timestamp, l_old=b'NotA-Class',
      l_new=b'Mid-Class', l_revision_timestamp=b'2018-01-01T12:00:00Z')
    logic_log.insert_or_update(self.wp10db, self.log)

  def test_timestamp_dt(self):
    dt = self.log.timestamp_dt
    self.assertEqual(2018, dt.year)
    self.assertEqual(4, dt.month)
    self.assertEqual(1, dt.day)
    self.assertEqual(12, dt.hour)
    self.assertEqual(30, dt.minute)
    self.assertEqual(0, dt.second)
