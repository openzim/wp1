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
      self.assertTrue(b'<title>WP 1.0 API</title>' in rv.data)

  def test_swagger_yml(self):
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/openapi.yml')
      self.assertTrue(b"title: 'WP 1.0 Frontend'" in rv.data)


class RqTest(unittest.TestCase):

  def setUp(self):
    os.environ['RQ_USER'] = 'testuser'
    os.environ['RQ_PASS'] = 'testpass'  # nosec

  def tearDown(self):
    del os.environ['RQ_USER']
    del os.environ['RQ_PASS']

  def test_rq_no_login(self):
    self.app = create_app()
    with self.app.test_client() as client:
      rv = client.get('/rq', follow_redirects=True)
      self.assertTrue(b'Please login' in rv.data)

  def test_rq_login(self):
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
