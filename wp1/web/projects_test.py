import json

from wp1.web.app import create_app
from wp1.web.base_web_testcase import BaseWebTestcase


class ProjectTest(BaseWebTestcase):

  def setUp(self):
    super().setUp()
    projects = []
    for i in range(101):
      projects.append({
          'p_project': b'Project %s' % str(i).encode('utf-8'),
          'p_timestamp': b'20181225'
      })

    with self.wp10db.cursor() as cursor:
      cursor.executemany(
          'INSERT INTO projects (p_project, p_timestamp) '
          'VALUES (%(p_project)s, %(p_timestamp)s)', projects)
    self.wp10db.commit()

  def test_list(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/')
      data = json.loads(rv.data)
      self.assertEqual(101, len(data))

  def test_count(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/projects/count')
      data = json.loads(rv.data)
      self.assertEqual(101, data['count'])
