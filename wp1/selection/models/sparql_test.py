import json
import unittest
from unittest.mock import patch, MagicMock

from wp1.selection.models.sparql import Builder as SparqlBuilder


class SparqlBuilderTest(unittest.TestCase):
  cats_uk_us_after_1950 = '''
    #Cats born in the UK or US after 1950
    SELECT ?cat
    WHERE
    {
      ?cat wdt:P31 wd:Q146;
          wdt:P569 ?birth.
      { ?cat wdt:P19 wd:Q30. }
      UNION
      { ?cat wdt:P19 wd:Q145. }
      FILTER(YEAR(?birth) > 1950)
    }
  '''

  json_return_value = {
      'results': {
          'bindings': [{
              'foo': {},
              '_wp1_0': {
                  'value': 'https://en.wikipedia.org/wiki/Foo'
              }
          }]
      }
  }

  expanded_query = (
      'SELECT ?cat ?_wp1_0{FILTER(YEAR(?birth) > '
      '"1950"^^<http://www.w3.org/2001/XMLSchema#integer>) ?cat '
      '<http://www.wikidata.org/prop/direct/P31> '
      '<http://www.wikidata.org/entity/Q146>.?cat '
      '<http://www.wikidata.org/prop/direct/P569> ?birth.OPTIONAL{?_wp1_0 <http://schema.org/isPartOf> '
      '<https://en.wikipedia.org/>.?_wp1_0 <http://schema.org/about> ?cat.}{?cat '
      '<http://www.wikidata.org/prop/direct/P19> '
      '<http://www.wikidata.org/entity/Q30>.OPTIONAL{?_wp1_0 <http://schema.org/isPartOf> '
      '<https://en.wikipedia.org/>.?_wp1_0 <http://schema.org/about> '
      '?cat.}}UNION{?cat <http://www.wikidata.org/prop/direct/P19> '
      '<http://www.wikidata.org/entity/Q145>.OPTIONAL{?_wp1_0 <http://schema.org/isPartOf> '
      '<https://en.wikipedia.org/>.?_wp1_0 <http://schema.org/about> ?cat.}}}')

  french_query = expanded_query.replace('en.wikipedia.org', 'fr.wikipedia.org')

  def setUp(self):
    self.builder = SparqlBuilder()

  @patch('wp1.selection.models.sparql.requests')
  def test_build(self, mock_requests):
    response = MagicMock()
    response.json.return_value = self.json_return_value
    mock_requests.post.return_value = response

    actual = self.builder.build('text/tab-separated-values',
                                project='en.wikipedia.org',
                                query=self.cats_uk_us_after_1950,
                                queryVariable='cat')

    mock_requests.post.assert_called_once_with(
        'https://query.wikidata.org/sparql',
        headers={
            'User-Agent': 'WP 1.0 bot 1.0.0/Audiodude <audiodude@gmail.com>'
        },
        data={
            'query': self.expanded_query,
            'format': 'json'
        })
    response.json.assert_called_once()
    self.assertEqual(b'Foo', actual)

  @patch('wp1.selection.models.sparql.requests')
  def test_build_french_wikipedia(self, mock_requests):
    response = MagicMock()
    response.json.return_value = self.json_return_value
    mock_requests.post.return_value = response

    actual = self.builder.build('text/tab-separated-values',
                                project='fr.wikipedia.org',
                                query=self.cats_uk_us_after_1950,
                                queryVariable='cat')

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
    self.assertEqual(b'Foo', actual)

  @patch('wp1.selection.models.sparql.requests')
  def test_build_server_error(self, mock_requests):
    response = MagicMock()
    mock_requests.post.return_value = response
    response.raise_for_status.side_effect = Exception()

    with self.assertRaises(Exception):
      actual = self.builder.build('text/tab-separated-values',
                                  query=self.cats_uk_us_after_1950,
                                  queryVariable='cat')

  @patch('wp1.selection.models.sparql.requests')
  def test_build_not_valid_json(self, mock_requests):
    response = MagicMock()
    response.json.side_effect = json.decoder.JSONDecodeError('foo', 'bar', 0)
    mock_requests.post.return_value = response

    with self.assertRaises(ValueError):
      actual = self.builder.build('text/tab-separated-values',
                                  query=self.cats_uk_us_after_1950,
                                  queryVariable='cat')

  @patch('wp1.selection.models.sparql.requests')
  def test_build_not_resp_too_large(self, mock_requests):
    response = MagicMock()
    response.content = 'a' * (1024 * 1024 * 20)
    mock_requests.post.return_value = response

    with self.assertRaises(ValueError):
      actual = self.builder.build('text/tab-separated-values',
                                  query=self.cats_uk_us_after_1950,
                                  queryVariable='cat')

  def test_validate(self):
    actual = self.builder.validate(query=self.cats_uk_us_after_1950)

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
    actual = self.builder.validate(query=query)

    self.assertEqual(('', query, ['Unknown namespace prefix : blah']), actual)
