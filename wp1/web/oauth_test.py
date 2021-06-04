from wp1.web.app import create_app
from wp1.web.oauth import identify
from wp1.web.base_web_testcase import BaseWebTestcase
from unittest import mock

from unittest.mock import patch


class IdentifyTest(BaseWebTestcase):

  def test_identify(self):
    self.app = create_app()
    self.app.testing = True
    with self.override_db(self.app), self.app.test_client() as c:
      with c.session_transaction() as sess:
        sess['user'] = {
            'access_token': 'abcd',
            'identity': {
                'username': 'mahakporwal02'
            }
        }
        assert identify() == {"username": 'mahakporwal02'}

  @mock.patch("wp1.web.oauth.session.get")
  def identify_test(self, mock_session_get):
    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      mock_session_get.return_value = mock.Mock({
          "access_code": 'abcd',
          "user": {
              "username": 'mahakporwal02'
          }
      })
      assert identify() == {"username": 'mahakporwal02'}

  def identify_test(self):
    self.app = create_app()
    self.app.testing = True
    with self.override_db(self.app), self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = {
            "access_code": 'abcd',
            "identity": {
                "username": 'mahakporwal02'
            }
        }
        rv = client.get('/v1/oauth/identify')
