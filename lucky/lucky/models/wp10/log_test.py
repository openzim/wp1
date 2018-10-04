from lucky.base_orm_test import BaseWpOneOrmTest
from lucky.models.wp10.log import Log

class ModelsLogTest(BaseWpOneOrmTest):
  def setUp(self):
    super().setUp()
    self.project_name = b'My test project'
    self.ns = 0
    self.article = b'The Art of Testing (book)'
    self.action = b'quality'
    self.timestamp = b'2018-04-01T12:30:00Z'
    self.log = Log(
      project=self.project_name, namespace=self.ns, article=self.article,
      action=self.action, timestamp=self.timestamp, old=b'NotA-Class',
      new=b'Mid-Class', revision_timestamp=b'2018-01-01T12:00:00Z')
    self.session.add(self.log)
    self.session.commit()

  def tearDown(self):
    self.session.delete(self.log)
    self.session.commit()

  def test_log_retrieval(self):
    actual = self.session.query(Log).get(
      [self.project_name, self.ns, self.article, self.action, self.timestamp])
    self.assertEqual(self.log, actual)

  def test_log_fields(self):
    actual = self.session.query(Log).get(
      [self.project_name, self.ns, self.article, self.action, self.timestamp])
    self.assertEqual(self.log.project, actual.project)
    self.assertEqual(self.log.namespace, actual.namespace)
    self.assertEqual(self.log.article, actual.article)
    self.assertEqual(self.log.action, actual.action)
    self.assertEqual(self.log.timestamp, actual.timestamp)
    self.assertEqual(self.log.old, actual.old)
    self.assertEqual(self.log.new, actual.new)
    self.assertEqual(self.log.revision_timestamp, actual.revision_timestamp)

  def test_timestamp_dt(self):
    dt = self.log.timestamp_dt
    self.assertEqual(2018, dt.year)
    self.assertEqual(4, dt.month)
    self.assertEqual(1, dt.day)
    self.assertEqual(12, dt.hour)
    self.assertEqual(30, dt.minute)
    self.assertEqual(0, dt.second)
