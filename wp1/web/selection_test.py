import unittest
from wp1.web.app import create_app
from wp1.web.base_web_testcase import BaseWebTestcase
from wp1.logic import selection
import json


class ProjectTest(unittest.TestCase):

  invalid_article_name = "Eiffel_Tower\nStatue of#Liberty"
  unsuccessful_response = {
      "status": "403",
      "success": False,
      "items": {
          'valid': ['Eiffel_Tower'],
          'invalid': ['Statue_of#Liberty'],
          'forbiden_chars': ['#']
      }
  }
  valid_article_name = "Eiffel_Tower\nStatue of Liberty"
  successful_response = {"status": "200", "success": True, "items": {}}

  def test_get_unsuccessful_article_name(self):
    self.app = create_app()
    with self.app.test_client() as client:
      rv = client.post('/v1/selection/',
                       json={'article_name': self.invalid_article_name})
      print(rv.get_json())
      self.assertEqual(rv.get_json(), self.unsuccessful_response)

  def test_get_article_name(self):
    self.app = create_app()
    with self.app.test_client() as client:
      rv = client.post('/v1/selection/',
                       json={'article_name': self.valid_article_name})
      print(rv.get_json())
      self.assertEqual(rv.get_json(), self.successful_response)
