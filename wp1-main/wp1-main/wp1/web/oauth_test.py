import unittest
from wp1.environment import Environment
from unittest.mock import patch, Mock
from wp1.web.app import create_app
from wp1.web.base_web_testcase import BaseWebTestcase
from wp1.web.db import get_db


class IdentifyTest(BaseWebTestcase):

  ENV = Environment.DEVELOPMENT
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
          'CLIENT_URL': {
              'domain': 'localhost:5173',
              'homepage': 'http://localhost:5173/#/'
          }
      },
      Environment.PRODUCTION: {}
  }
  REDIRECT = 'https://en.wikipedia.org/w/index.php?oauth_token=token&oauth_consumer_key=key'
  USER = {
      'access_token': 'access_token',
      'identity': {
          'username': 'WP1_user',
          'sub': '1234'
      }
  }
  REQUEST_TOKEN = {'key': 'request_token', 'secret': 'request_token_secret'}
  handshaker = Mock(
      **{
          'initiate.return_value': (REDIRECT, REQUEST_TOKEN),
          'complete.return_value': {
              'key': 'access_token',
              'secret': 'access_secret'
          },
          'identify.return_value': USER['identity']
      })

  @patch('wp1.web.app.ENV', Environment.DEVELOPMENT)
  @patch('wp1.web.app.CREDENTIALS', TEST_OAUTH_CREDS)
  @patch('wp1.web.oauth.homepage_url',
         TEST_OAUTH_CREDS[ENV]['CLIENT_URL']['homepage'])
  def test_initiate_authorized_user(self):
    self.app = create_app()
    with self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.get('/v1/oauth/initiate')
      self.assertEqual(
          self.TEST_OAUTH_CREDS[self.ENV]['CLIENT_URL']['homepage'],
          rv.location)

  @patch('wp1.web.app.ENV', Environment.DEVELOPMENT)
  @patch('wp1.web.app.CREDENTIALS', TEST_OAUTH_CREDS)
  @patch('wp1.web.oauth.handshaker', handshaker)
  def test_initiate_unauthorized_user(self):
    self.app = create_app()
    with self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['request_token'] = self.REQUEST_TOKEN
      rv = client.get('/v1/oauth/initiate')
      self.assertEqual(self.REDIRECT, rv.location)

  @patch('wp1.web.app.ENV', Environment.DEVELOPMENT)
  @patch('wp1.web.app.CREDENTIALS', TEST_OAUTH_CREDS)
  @patch('wp1.web.oauth.homepage_url',
         TEST_OAUTH_CREDS[ENV]['CLIENT_URL']['homepage'])
  def test_initiate_authorized_user_with_next_path(self):
    self.app = create_app()
    with self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.get('/v1/oauth/initiate?next=update')
      self.assertEqual(
          f"{self.TEST_OAUTH_CREDS[self.ENV]['CLIENT_URL']['homepage']}update",
          rv.location)

  @patch('wp1.web.app.ENV', Environment.DEVELOPMENT)
  @patch('wp1.web.app.CREDENTIALS', TEST_OAUTH_CREDS)
  def test_complete_unauthorized_user(self):
    self.app = create_app()
    with self.app.test_client() as client:
      rv = client.get('/v1/oauth/complete')
      self.assertEqual('404 NOT FOUND', rv.status)

  @patch('wp1.web.app.ENV', Environment.DEVELOPMENT)
  @patch('wp1.web.app.CREDENTIALS', TEST_OAUTH_CREDS)
  @patch('wp1.web.oauth.homepage_url',
         TEST_OAUTH_CREDS[ENV]['CLIENT_URL']['homepage'])
  @patch('wp1.web.oauth.handshaker', handshaker)
  def test_complete_authorized_user(self):
    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['request_token'] = self.REQUEST_TOKEN
        sess['next_path'] = ''
      rv = client.get('/v1/oauth/complete?query_string')
      self.assertEqual(
          self.TEST_OAUTH_CREDS[self.ENV]['CLIENT_URL']['homepage'],
          rv.location)
      wp10db = get_db('wp10db')
      with wp10db.cursor() as cursor:
        cursor.execute('SELECT * FROM users WHERE u_id = 1234')
        self.assertNotEqual(None, cursor.fetchone())

  @patch('wp1.web.app.ENV', Environment.DEVELOPMENT)
  @patch('wp1.web.app.CREDENTIALS', TEST_OAUTH_CREDS)
  @patch('wp1.web.oauth.homepage_url',
         TEST_OAUTH_CREDS[ENV]['CLIENT_URL']['homepage'])
  @patch('wp1.web.oauth.handshaker', handshaker)
  def test_complete_authorized_user_with_next_path(self):
    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['request_token'] = self.REQUEST_TOKEN
        sess['next_path'] = 'update'
      rv = client.get('/v1/oauth/complete?query_string')
      self.assertEqual(
          f"{self.TEST_OAUTH_CREDS[self.ENV]['CLIENT_URL']['homepage']}update",
          rv.location)
      wp10db = get_db('wp10db')
      with wp10db.cursor() as cursor:
        cursor.execute('SELECT * FROM users WHERE u_id = 1234')
        self.assertNotEqual(None, cursor.fetchone())

  @patch('wp1.web.app.CREDENTIALS', TEST_OAUTH_CREDS)
  @patch('wp1.web.app.ENV', Environment.DEVELOPMENT)
  def test_identify_authorized_user(self):
    self.app = create_app()
    with self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
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
        sess['user'] = self.USER
        sess['next_path'] = '/'
      rv = client.get('/v1/oauth/logout')
      self.assertEqual({'status': '204'}, rv.get_json())

  @patch('wp1.web.app.CREDENTIALS', TEST_OAUTH_CREDS)
  @patch('wp1.web.app.ENV', Environment.DEVELOPMENT)
  def test_logout_unauthorized_user(self):
    self.app = create_app()
    with self.app.test_client() as client:
      rv = client.get('/v1/oauth/logout')
      self.assertEqual('404 NOT FOUND', rv.status)
