import json
import unittest
from unittest.mock import patch, MagicMock

import requests

from wp1.base_db_test import BaseWpOneDbTest, get_first_selection
from wp1.exceptions import Wp1FatalSelectionError, Wp1RetryableSelectionError
from wp1.models.wp10.builder import Builder
from wp1.selection.models.sparql import Builder as SparqlBuilder


class SparqlBuilderTest(BaseWpOneDbTest):
  cats_uk_us_after_1950 = '''
    #Cats born in the UK or US after 1950
    SELECT ?cat
    WHERE
    {
      ?cat wdt:P31 wd:Q146;
          wdt:P569 ?birth.
      ?url schema:isPartOf <https://en.wikipedia.org/> .
      ?url schema:about ?cat .
      { ?cat wdt:P19 wd:Q30. }
      UNION
      { ?cat wdt:P19 wd:Q145. }
      FILTER(YEAR(?birth) > 1950)
    }
  '''

  french_query = cats_uk_us_after_1950.replace('en.wikipedia.org',
                                               'fr.wikipedia.org')

  json_return_value = {
      'results': {
          'bindings': [{
              'cat': {
                  'value': 'Sparkles'
              },
              'birth': {
                  'value': '1960-01-01'
              },
              'url': {
                  'value': 'https://en.wikipedia.org/wiki/Foo'
              }
          }, {
              'cat': {
                  'value': 'Sprinkles'
              },
              'birth': {
                  'value': '1965-01-01'
              },
              'url': {
                  'value': 'https://en.wikipedia.org/wiki/B%C3%A5r'
              }
          }]
      }
  }

  french_return_value = {
      'results': {
          'bindings': [{
              'cat': {
                  'value': 'Sparkles'
              },
              'birth': {
                  'value': '1960-01-01'
              },
              'url': {
                  'value': 'https://fr.wikipedia.org/wiki/Foo'
              }
          }, {
              'cat': {
                  'value': 'Sprinkles'
              },
              'birth': {
                  'value': '1965-01-01'
              },
              'url': {
                  'value': 'https://fr.wikipedia.org/wiki/B%C3%A5r'
              }
          }]
      }
  }

  def setUp(self):
    super().setUp()
    self.s3 = MagicMock()
    self.builder_model = Builder(b_id=b'1a-2b-3c-4d',
                                 b_name=b'SPARQL Builder',
                                 b_user_id=1234,
                                 b_project=b'en.wikipedia.fake',
                                 b_model=b'wp1.selection.models.sparql',
                                 b_params=json.dumps({
                                     'query': self.cats_uk_us_after_1950,
                                 }).encode('utf-8'))
    self.builder = SparqlBuilder()

  @patch('wp1.selection.models.sparql.requests')
  def test_materialize(self, mock_requests):
    response = MagicMock()
    response.json.return_value = self.json_return_value
    mock_requests.post.return_value = response

    self.builder.materialize(self.s3, self.wp10db, self.builder_model,
                             'text/tab-separated-values', 1)

    actual = get_first_selection(self.wp10db)
    self.assertEqual(b'text/tab-separated-values', actual.s_content_type)
    self.assertEqual(b'1a-2b-3c-4d', actual.s_builder_id)

  @patch('wp1.selection.models.sparql.requests')
  def test_build(self, mock_requests):
    response = MagicMock()
    response.json.return_value = self.json_return_value
    mock_requests.post.return_value = response

    actual = self.builder.build('text/tab-separated-values',
                                project='en.wikipedia.org',
                                query=self.cats_uk_us_after_1950)

    mock_requests.post.assert_called_once_with(
        'https://query.wikidata.org/sparql',
        headers={
            'User-Agent': 'WP 1.0 bot 1.0.0/Audiodude <audiodude@gmail.com>'
        },
        data={
            'query': self.cats_uk_us_after_1950,
            'format': 'json'
        })
    response.json.assert_called_once()
    self.assertEqual('Foo\nBår'.encode('utf-8'), actual)

  @patch('wp1.selection.models.sparql.requests')
  def test_build_french_wikipedia(self, mock_requests):
    response = MagicMock()
    response.json.return_value = self.french_return_value
    mock_requests.post.return_value = response

    actual = self.builder.build('text/tab-separated-values',
                                project='fr.wikipedia.org',
                                query=self.french_query)

    mock_requests.post.assert_called_once_with(
        'https://query.wikidata.org/sparql',
        headers={
            'User-Agent': 'WP 1.0 bot 1.0.0/Audiodude <audiodude@gmail.com>'
        },
        data={
            'query': self.french_query,
            'format': 'json'
        })
    response.json.assert_called_once()
    self.assertEqual('Foo\nBår'.encode('utf-8'), actual)

  def test_build_wrong_content_type(self):
    with self.assertRaises(Wp1FatalSelectionError):
      actual = self.builder.build(None,
                                  query=self.cats_uk_us_after_1950,
                                  queryVariable='cat')

  def test_build_missing_query(self):
    with self.assertRaises(Wp1FatalSelectionError):
      actual = self.builder.build('text/tab-separated-values',
                                  project='en.wikipedia.org',
                                  queryVariable='cat')

  @patch('wp1.selection.models.sparql.requests.post')
  def test_build_server_error(self, mock_request_post):
    response = MagicMock()
    mock_request_post.return_value = response
    response.raise_for_status.side_effect = requests.exceptions.HTTPError

    with self.assertRaises(Wp1FatalSelectionError):
      actual = self.builder.build('text/tab-separated-values',
                                  project='en.wikipedia.org',
                                  query=self.cats_uk_us_after_1950,
                                  queryVariable='cat')

  @patch('wp1.selection.models.sparql.requests.post')
  def test_build_server_timeout(self, mock_request_post):
    response = MagicMock()
    mock_request_post.side_effect = requests.exceptions.Timeout

    with self.assertRaises(Wp1RetryableSelectionError):
      actual = self.builder.build('text/tab-separated-values',
                                  project='en.wikipedia.org',
                                  query=self.cats_uk_us_after_1950,
                                  queryVariable='cat')

  @patch('wp1.selection.models.sparql.requests.post')
  def test_build_server_request_exception(self, mock_request_post):
    response = MagicMock()
    mock_request_post.side_effect = requests.exceptions.RequestException

    with self.assertRaises(Wp1RetryableSelectionError):
      actual = self.builder.build('text/tab-separated-values',
                                  project='en.wikipedia.org',
                                  query=self.cats_uk_us_after_1950,
                                  queryVariable='cat')

  @patch('wp1.selection.models.sparql.requests.post')
  def test_build_not_valid_json(self, mock_request_post):
    response = MagicMock()
    response.json.side_effect = json.decoder.JSONDecodeError('foo', 'bar', 0)
    mock_request_post.return_value = response

    with self.assertRaises(Wp1FatalSelectionError):
      actual = self.builder.build('text/tab-separated-values',
                                  project='en.wikipedia.org',
                                  query=self.cats_uk_us_after_1950,
                                  queryVariable='cat')

  @patch('wp1.selection.models.sparql.requests.post')
  def test_build_not_resp_too_large(self, mock_request_post):
    response = MagicMock()
    response.content = 'a' * (1024 * 1024 * 20)
    mock_request_post.return_value = response

    with self.assertRaises(Wp1FatalSelectionError):
      actual = self.builder.build('text/tab-separated-values',
                                  project='en.wikipedia.org',
                                  query=self.cats_uk_us_after_1950,
                                  queryVariable='cat')

  def test_validate(self):
    actual = self.builder.validate(query=self.cats_uk_us_after_1950,
                                   project='en.wikipedia.org',
                                   queryVariable='cat')

    self.assertEqual(('', '', []), actual)

  def test_validate_no_parse(self):
    invalid_queries = [
        'Hello World!',
        'SELECT blah blah foo',
        'SELECT ?foo',
        'SELECT ?foo FROM bar',
        'SELECT ?foo WHERE ?foo wdt:P19 ?bar',
        'SELECT ?foo WHERE { ?foo wdt:P19 ?bar ?baz. }',
        'SELECT ?foo WHERE { {?foo wdt:P19 ?bar.} UNION { ?baz.} }',
    ]

    for query in invalid_queries:
      actual = self.builder.validate(query=query)

      self.assertEqual(
          ('', query,
           ['Could not parse query, are you sure it\'s valid SPARQL?']), actual)

  def test_validate_missing_prefix(self):
    query = 'SELECT ?foo WHERE { ?foo blah:x ?bar }'
    actual = self.builder.validate(project='en.wikipedia.org',
                                   query=query,
                                   queryVariable='foo')

    self.assertEqual(('', query, ['Unknown namespace prefix : blah']), actual)
