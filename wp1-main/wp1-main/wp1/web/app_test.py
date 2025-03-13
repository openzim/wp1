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
