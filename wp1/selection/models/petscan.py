import logging
import urllib

import requests
import validators

from wp1.constants import WP1_USER_AGENT
from wp1.exceptions import Wp1FatalSelectionError
from wp1.selection.abstract_builder import AbstractBuilder

logger = logging.getLogger(__name__)


class Builder(AbstractBuilder):

  def build(self, content_type, **params):
    if content_type != 'text/tab-separated-values':
      raise Wp1FatalSelectionError('Unrecognized content type')
    if 'url' not in params:
      raise Wp1FatalSelectionError('Missing required param: url')
    if not isinstance(params['url'], str):
      raise Wp1FatalSelectionError('Param `url` was not str')

    # Set the result data format to json
    parsed_url = urllib.parse.urlparse(params['url'])
    parsed_query = urllib.parse.parse_qs(parsed_url.query)
    parsed_query['format'] = ['json']
    final_url = parsed_url._replace(
        query=urllib.parse.urlencode(parsed_query, doseq=True)).geturl()

    resp = requests.get(final_url, headers={'User-Agent': WP1_USER_AGENT})
    try:
      resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
      logger.exception('Error status received from Petscan server')
      raise Wp1FatalSelectionError('Error status from Petscan server') from e

    data = resp.json()
    titles = [item['title'] for item in data['*'][0]['a']['*']]
    return '\n'.join(titles).encode('utf-8')

  def validate(self, **params):
    if 'url' not in params:
      return ('', '', ['Missing URL parameter'])

    if not validators.url(params['url']):
      return ('', params['url'], ['That doesn\'t look like a valid URL.'])

    parsed_url = urllib.parse.urlparse(params['url'])
    if 'petscan.wmflabs.org' not in parsed_url.netloc:
      return ('', params['url'],
              ['Only URLs that lead to petscan.wmflabs.org are allowed.'])

    return ('', '', [])
