import json
import urllib.parse

from pyparsing.exceptions import ParseException
import requests
from rdflib.term import Literal, URIRef, Variable
from rdflib.plugins.sparql import algebra
from rdflib.plugins.sparql import parser
from rdflib.plugins.sparql.parserutils import CompValue

from wp1.constants import WIKIDATA_PREFIXES, WP1_USER_AGENT
from wp1.exceptions import Wp1RetryableSelectionError, Wp1FatalSelectionError
from wp1.selection.abstract_builder import AbstractBuilder


class Builder(AbstractBuilder):
  '''
  Model for validating and building (materializing) SPARQL builders.

  A SPARQL list is a SPARQL query that represents a list of articles.

  The 'validate' method takes in the parameters to the model in kwargs format
  and returns a tuple of three items: A list with the valid values, a list with
  the invalid values, and a list of error messages. So ([], [], []). If the
  second or third items are truthy, it is considered an error.

  The 'build' method takes in the same parameters and materializes the builder
  into a selection. This means taking those parameters and producing a newline
  separated string which represents an article list, that will be uploaded
  directly to S3-like storage as the selection contents.

  Both of these methods are called by the backend API and the AbstractBuilder
  abstract class.
  '''

  def _article_id_from_url(self, url):
    return urllib.parse.unquote(url.split('/')[-1])

  def _extract_articles(self, project, query, data):
    '''
    Method for getting article ids from the query results.

    Takes the project that the query is for (like 'en.wikipedia.org'), the
    original query, and the data returned from the SPARQL endpoint.
    '''
    # Parse the query so we can extract the variables that appear in it.
    parse_results = parser.parseQuery(query)
    q = algebra.translateQuery(parse_results, initNs=WIKIDATA_PREFIXES)

    urls = []
    # Check every variable that appears in the query graph.
    for variable in [str(v) for v in q.algebra._vars]:
      has_struct = len(data.get('results', {}).get('bindings', [])) > 0
      if not has_struct:
        continue
      if not data['results']['bindings'][0].get(variable):
        # There is no binding for this variable. Maybe it's some kind of
        # special variable. Just skip it.
        continue
      test_url = data['results']['bindings'][0][variable]['value']
      if project in test_url:
        # If the project, which is a URL, appears in the binding, it's probably
        # an article URL on that project's site. Collect all the urls and break
        # because we've got the list.
        urls = [
            d[variable]['value']
            for d in data['results']['bindings']
            if variable in d
        ]
        break

    # The final return value is the article ID for each url.
    return [self._article_id_from_url(url) for url in urls]

  def build(self, content_type, **params):
    if content_type != 'text/tab-separated-values':
      raise Wp1FatalSelectionError('Unrecognized content type')

    project = params.get('project')
    if not project:
      raise Wp1FatalSelectionError('Expected param "project", got: %r' %
                                   project)

    params_query = params.get('query')
    if not params_query:
      raise Wp1FatalSelectionError('Expected param "query", got: %r' %
                                   params_query)

    try:
      r = requests.post('https://query.wikidata.org/sparql',
                        headers={'User-Agent': WP1_USER_AGENT},
                        data={
                            'query': params_query,
                            'format': 'json',
                        })
    except requests.exceptions.Timeout as e:
      raise Wp1RetryableSelectionError(
          'The request to Wikidata timed out') from e
    except requests.exceptions.RequestException as e:
      raise Wp1RetryableSelectionError('Could not connect to Wikidata') from e

    try:
      r.raise_for_status()
    except requests.exceptions.HTTPError as e:
      raise Wp1FatalSelectionError(
          f'Wikidata sent back a non-200 status code: {r.status_code}') from e

    try:
      data = r.json()
    except json.decoder.JSONDecodeError:
      raise Wp1FatalSelectionError(
          'Wikidata response was not valid JSON. This is usually caused '
          'by a timeout because the result set is too large.') from None

    if len(r.content) > 1024 * 1024 * 10:
      raise Wp1FatalSelectionError('Wikidata response was larger than 10 MB')

    articles = self._extract_articles(project, params_query, data)

    if articles:
      return '\n'.join(articles).encode('utf-8')

    raise Wp1FatalSelectionError(
        'Did not find any articles in query results. Make sure you are selecting '
        'a ?url in your query using the "schema:about" predicate, and that you are '
        'using the schema:isPartOf predicate to limit your URLs to a project that '
        'matches the project you selected on the Selection edit screen. '
        'For more information, check the WP1 end user documentation.')

  def validate(self, **params):
    try:
      parse_results = parser.parseQuery(params['query'])
    except ParseException as pe:
      # The query cannot be parsed as SPARQL, invalid syntax.
      return ('', params['query'],
              ['Could not parse query, are you sure it\'s valid SPARQL?'])
    try:
      query = algebra.translateQuery(parse_results, initNs=WIKIDATA_PREFIXES)
    except Exception as e:
      # In testing, this was most common when the query contained
      # an undefined prefix.
      return ('', params['query'], [str(e)])

    return ('', '', [])
