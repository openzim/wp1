from wp1.web.app import app
from wp1.web.base_web_testcase import BaseWebTestcase


class AppTest(BaseWebTestcase):

  def test_index(self):
    with self.override_db(app), app.test_client() as client:
      rv = client.get('/')
      self.assertTrue(b'Wikipedia 1.0 Server' in rv.data)

  def test_index_project_count(self):
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

    with self.override_db(app), app.test_client() as client:
      rv = client.get('/')
      print(rv.data)
      self.assertTrue(b'There are currently 101 projects being tracked '
                      b'and updated each day.' in rv.data)
