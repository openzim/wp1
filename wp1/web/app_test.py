from wp1.web.app import app
from wp1.web.base_web_testcase import BaseWebTestcase


class AppTest(BaseWebTestcase):

  def test_index(self):
    with self._override_db(app), app.test_client() as client:
      rv = client.get('/')
      self.assertTrue(b'Wikipedia 1.0 Server' in rv.data)
