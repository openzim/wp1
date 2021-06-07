import unittest
from wp1.web.app import create_app
from wp1.environment import Environment
from unittest.mock import patch


class IdentifyTest(unittest.TestCase):

  TEST_OAUTH_CREDS = {
      Environment.DEVELOPMENT: {
          'API': {},
          'MWOAUTH': {
              'consumer_key': 'consumer_key',
              'consumer_secret': 'consumer_secret'
          },
          'SESSION': {
              'secret_key': 'wp1_secret'
          },
          'CLIENT_URL': 'http://localhost:3000/#/'
      },
      Environment.PRODUCTION: {}
  }

  @patch('wp1.web.app.CREDENTIALS', TEST_OAUTH_CREDS)
  @patch('wp1.web.app.ENV', Environment.DEVELOPMENT)
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

  @patch('wp1.web.app.CREDENTIALS', TEST_OAUTH_CREDS)
  @patch('wp1.web.app.ENV', Environment.DEVELOPMENT)
  def test_identify_unauthorized_user(self):
    self.app = create_app()
    with self.app.test_client() as client:
      rv = client.get('/v1/oauth/identify')
      self.assertEqual('401 UNAUTHORIZED', rv.status)

  @patch('wp1.web.app.CREDENTIALS', TEST_OAUTH_CREDS)
  @patch('wp1.web.app.ENV', Environment.DEVELOPMENT)
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

  @patch('wp1.web.app.CREDENTIALS', TEST_OAUTH_CREDS)
  @patch('wp1.web.app.ENV', Environment.DEVELOPMENT)
  def test_logout_unauthorized_user(self):
    self.app = create_app()
    with self.app.test_client() as client:
      rv = client.get('/v1/oauth/logout')
      self.assertEqual('404 NOT FOUND', rv.status)
