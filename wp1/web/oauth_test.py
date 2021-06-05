from wp1.web.app import create_app
from wp1.web.base_web_testcase import BaseWebTestcase
import unittest

try:
  from wp1.credentials import ENV, CREDENTIALS
except ImportError:
  ENV = None
  CREDENTIALS = None

missing_credentials = CREDENTIALS is None or ENV is None
if not missing_credentials:
  mwoauth = CREDENTIALS.get("ENV", {}).get("MWOAUTH", {})
if missing_credentials or mwoauth.get('consumer_key') is None or mwoauth.get(
    'consumer_secret') is None:
  mwoauth = {
      'consumer_key': 'consumer_key',
      'consumer_secret': 'consumer_secret'
  }


class IdentifyTest(BaseWebTestcase):

  def test_identify_authorized_user(self):
    self.app = create_app()
    with self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = {
            'access_token': 'access_token',
            'identity': {
                'username': 'WP1_user'
            }
        }
      rv = client.get('/v1/oauth/identify')
      self.assertEqual({"username": 'WP1_user'}, rv.get_json())

  def test_identify_unauthorized_user(self):
    self.app = create_app()
    with self.app.test_client() as client:
      rv = client.get('/v1/oauth/identify')
      self.assertEqual('401 UNAUTHORIZED', rv.status)

  def test_logout_authorized_user(self):
    self.app = create_app()
    with self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = {
            'access_token': 'access_token',
            'identity': {
                'username': 'WP1_user'
            }
        }
      rv = client.get('/v1/oauth/logout')
      self.assertEqual({'status': '204'}, rv.get_json())

  def test_logout_unauthorized_user(self):
    self.app = create_app()
    with self.app.test_client() as client:
      rv = client.get('/v1/oauth/logout')
      self.assertEqual('404 NOT FOUND', rv.status)
