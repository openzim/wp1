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
    self.assertEquals(self.project, actual)

  def test_project_fields(self):
    actual = self.session.query(Project).get(self.project_name)
    self.assertEquals(self.project.project, actual.project)
    self.assertEquals(self.project.timestamp, actual.timestamp)
    self.assertEquals(self.project.count, actual.count)
    self.assertEquals(
      self.project.upload_timestamp, actual.upload_timestamp)

  def test_timestamp_dt(self):
    dt = self.project.timestamp_dt
    self.assertEquals(2018, dt.year)
    self.assertEquals(9, dt.month)
    self.assertEquals(30, dt.day)
    self.assertEquals(12, dt.hour)
    self.assertEquals(30, dt.minute)
    self.assertEquals(0, dt.second)
