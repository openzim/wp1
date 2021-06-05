from wp1.web.app import create_app
from wp1.web.base_web_testcase import BaseWebTestcase
import unittest

try:
  # The credentials module isn't checked in and may be missing
  from wp1.credentials import ENV, CREDENTIALS
except ImportError:
  ENV = None
  CREDENTIALS = None

if (CREDENTIALS is None or CREDENTIALS[ENV].get('MWOAUTH') is None or
    CREDENTIALS[ENV]['MWOAUTH'].get('consumer_key') is None or
    CREDENTIALS[ENV]['MWOAUTH'].get('consumer_secret') is None):
  Skip = True
else:
  Skip = False


@unittest.skipIf(Skip, 'Cannot find Credentials.py')
class IdentifyTest(BaseWebTestcase):

  def test_identify(self):
    self.app = create_app()
    self.app.testing = True
    with self.app.test_client() as client:
      rv = client.get('/v1/oauth/identify')
      self.assertEqual('401 UNAUTHORIZED', rv.status)
      with client.session_transaction() as sess:
        sess['user'] = {
            'access_token': 'access_token',
            'identity': {
                'username': 'WP1_user'
            }
        }
      rv = client.get('/v1/oauth/identify')
      self.assertEqual({"username": 'WP1_user'}, rv.get_json())

  def test_logout(self):
    self.app = create_app()
    self.app.testing = True
    with self.app.test_client() as client:
      rv = client.get('/v1/oauth/logout')
      self.assertEqual('404 NOT FOUND', rv.status)
      with client.session_transaction() as sess:
        sess['user'] = {
            'access_token': 'access_token',
            'identity': {
                'username': 'WP1_user'
            }
        }
      rv = client.get('/v1/oauth/logout')
      self.assertEqual({'status': '204'}, rv.get_json())
