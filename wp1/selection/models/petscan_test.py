from unittest.mock import MagicMock, patch

from wp1.base_db_test import BaseWpOneDbTest, get_first_selection
from wp1.exceptions import Wp1FatalSelectionError
from wp1.models.wp10.builder import Builder
from wp1.selection.models.petscan import Builder as PetscanBuilder

import requests


class PetscanBuilderTest(BaseWpOneDbTest):
  mock_petscan_response = {
      '*': [{
          'a': {
              '*': [{
                  'title': 'Foo'
              }, {
                  'title': 'Bar'
              }]
          }
      }]
  }

  def setUp(self):
    super().setUp()
    self.s3 = MagicMock()
    self.builder_model = Builder(
        b_id=b'1a-2b-3c-4d',
        b_name=b'Petscan Builder',
        b_user_id=1234,
        b_project=b'en.wikipedia.fake',
        b_model=b'wp1.selection.models.petscan',
        b_params='{"url":"https://petscan.wmflabs.org/?psid=552"}')
    self.builder = PetscanBuilder()

  @patch('wp1.selection.models.petscan.requests')
  def test_materialize(self, mock_requests):
    self.builder.materialize(self.s3, self.wp10db, self.builder_model,
                             'text/tab-separated-values', 1)
    actual = get_first_selection(self.wp10db)
    self.assertEqual(actual.s_content_type, b'text/tab-separated-values')
    self.assertEqual(actual.s_builder_id, b'1a-2b-3c-4d')

  @patch('wp1.selection.models.petscan.requests')
  def test_build(self, mock_requests):
    mock_response = MagicMock()
    mock_response.json.return_value = self.mock_petscan_response
    mock_requests.get.return_value = mock_response

    actual = self.builder.build('text/tab-separated-values',
                                url='https://petscan.wmflabs.org.fake/?psid=42')
    self.assertEqual(b'Foo\nBar', actual)

  def test_build_wrong_content_type(self):
    with self.assertRaises(Wp1FatalSelectionError):
      actual = self.builder.build(
          None, url='https://petscan.wmflabs.org.fake/?psid=42')

  def test_build_missing_url(self):
    with self.assertRaises(Wp1FatalSelectionError):
      actual = self.builder.build('text/tab-separated-values')

  def test_build_url_not_str(self):
    with self.assertRaises(Wp1FatalSelectionError):
      actual = self.builder.build(
          'text/tab-separated-values',
          url=['https://petscan.wmflabs.org.fake/?psid=42'])

  @patch('wp1.selection.models.petscan.requests')
  def test_build_no_format(self, mock_requests):
    mock_response = MagicMock()
    mock_response.json.return_value = self.mock_petscan_response
    mock_requests.get.return_value = mock_response

    actual = self.builder.build('text/tab-separated-values',
                                url='https://petscan.wmflabs.org.fake/?psid=42')
    mock_requests.get.assert_called_with(
        'https://petscan.wmflabs.org.fake/?psid=42&format=json',
        headers={
            'User-Agent': 'WP 1.0 bot 1.0.0/Audiodude <audiodude@gmail.com>'
        })

  @patch('wp1.selection.models.petscan.requests')
  def test_build_other_format(self, mock_requests):
    mock_response = MagicMock()
    mock_response.json.return_value = self.mock_petscan_response
    mock_requests.get.return_value = mock_response

    actual = self.builder.build(
        'text/tab-separated-values',
        url='https://petscan.wmflabs.org.fake/?psid=42&format=wiki')
    mock_requests.get.assert_called_with(
        'https://petscan.wmflabs.org.fake/?psid=42&format=json',
        headers={
            'User-Agent': 'WP 1.0 bot 1.0.0/Audiodude <audiodude@gmail.com>'
        })

  @patch('wp1.selection.models.petscan.requests.get')
  def test_build_non_200(self, mock_requests_get):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
    mock_requests_get.return_value = mock_response

    with self.assertRaises(Wp1FatalSelectionError):
      actual = self.builder.build(
          'text/tab-separated-values',
          url='https://petscan.wmflabs.org.fake/?psid=42')

  def test_validate(self):
    actual = self.builder.validate(
        url='https://petscan.wmflabs.org.fake/?psid=42&format=wiki')
    self.assertEqual(('', '', []), actual)

  def test_validate_missing_url(self):
    actual = self.builder.validate()
    self.assertEqual(('', '', ['Missing URL parameter']), actual)

  def test_validate_not_a_url(self):
    actual = self.builder.validate(url='http:// foo bar [baz]')
    self.assertEqual(
        ('', 'http:// foo bar [baz]', ['That doesn\'t look like a valid URL.']),
        actual)

  def test_validate_not_a_petscan_url(self):
    actual = self.builder.validate(url='http://en.wikipedia.org/')
    self.assertEqual(
        ('', 'http://en.wikipedia.org/',
         ['Only URLs that lead to petscan.wmflabs.org are allowed.']), actual)
