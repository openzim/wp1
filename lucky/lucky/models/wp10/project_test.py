from lucky.base_orm_test import BaseWpOneOrmTest
from lucky.models.wp10.project import Project

class ModelsProjectTest(BaseWpOneOrmTest):
  def setUp(self):
    super().setUp()
    self.project_name = b'My test project'
    self.project = Project(
      project=self.project_name, timestamp=b'2018-09-30T12:30:00Z', count=100,
      upload_timestamp=b'20180-09-29T12:00:00Z')
    self.session.add(self.project)
    self.session.commit()

  def tearDown(self):
    self.session.delete(self.project)
    self.session.commit()

  def test_project_retrieval(self):
    actual = self.session.query(Project).get(self.project_name)
    self.assertEqual(self.project, actual)

  def test_project_fields(self):
    actual = self.session.query(Project).get(self.project_name)
    self.assertEqual(self.project.project, actual.project)
    self.assertEqual(self.project.timestamp, actual.timestamp)
    self.assertEqual(self.project.count, actual.count)
    self.assertEqual(
      self.project.upload_timestamp, actual.upload_timestamp)

  def test_timestamp_dt(self):
    dt = self.project.timestamp_dt
    self.assertEqual(2018, dt.year)
    self.assertEqual(9, dt.month)
    self.assertEqual(30, dt.day)
    self.assertEqual(12, dt.hour)
    self.assertEqual(30, dt.minute)
    self.assertEqual(0, dt.second)
