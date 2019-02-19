from lucky.base_db_test import BaseWpOneDbTest
from lucky.logic import project as logic_project
from lucky.models.wp10.project import Project

class ModelsProjectTest(BaseWpOneDbTest):
  def setUp(self):
    super().setUp()
    self.project_name = b'My test project'
    self.project = Project(
      p_project=self.project_name, p_timestamp=b'20180930123000', p_count=100,
      p_upload_timestamp=b'20180929120000')
    logic_project.insert_or_update(self.wp10db, self.project)

  def test_timestamp_dt(self):
    dt = self.project.timestamp_dt
    self.assertEqual(2018, dt.year)
    self.assertEqual(9, dt.month)
    self.assertEqual(30, dt.day)
    self.assertEqual(12, dt.hour)
    self.assertEqual(30, dt.minute)
    self.assertEqual(0, dt.second)
