from base64 import b64encode
import json
import os
import unittest
from unittest.mock import patch

from wp1.web.app import create_app
from wp1.web.base_web_testcase import BaseWebTestcase


class AppTest(BaseWebTestcase):

  def test_index(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/')
      self.assertTrue(b'Wikipedia 1.0 Server' in rv.data)


class RqTest(unittest.TestCase):

  @patch('wp1.web.app.get_redis_creds')
  def test_rq_no_login(self, patched_get_creds):
    patched_get_creds.return_value = {
        'host': 'localhost',
        'port': 6379,
    }
    os.environ['RQ_USER'] = 'testuser'
    os.environ['RQ_PASS'] = 'testpass'  # nosec
    self.app = create_app()
    with self.app.test_client() as client:
      rv = client.get('/rq', follow_redirects=True)
      self.assertTrue(b'Please login' in rv.data)

  @patch('wp1.web.app.get_redis_creds')
  def test_rq_login(self, patched_get_creds):
    patched_get_creds.return_value = {
        'host': 'localhost',
        'port': 6379,
    }
    os.environ['RQ_USER'] = 'testuser'
    os.environ['RQ_PASS'] = 'testpass'  # nosec
    self.app = create_app()
    with self.app.test_client() as client:
      rv = client.get(
          '/rq',
          headers={
              'Authorization':
                  'Basic {}'.format(
                      b64encode(b'testuser:testpass').decode('utf-8'))
          },
          follow_redirects=True)
      self.assertFalse(b'Please login' in rv.data)
