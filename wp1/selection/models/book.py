import logging
import urllib

import mwparserfromhell
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
    if 'project' not in params:
      raise Wp1FatalSelectionError('Missing required param: project')

    if not isinstance(params['url'], str):
      raise Wp1FatalSelectionError('Param `url` was not str')
    if not isinstance(params['project'], str):
      raise Wp1FatalSelectionError('Param `project` was not str')

    book_name = params['url'].split('wiki/')[1]
    final_url = (
        'https://%s/w/api.php?'
        'action=query&prop=revisions&rvprop=content&format=json&rvslots=main'
        '&titles=%s' % (params['project'], book_name))

    resp = requests.get(final_url, headers={'User-Agent': WP1_USER_AGENT})
    try:
      resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
      logger.exception('Error status received from Wikipedia API')
      raise Wp1FatalSelectionError(
          'Error status received from Wikipedia API') from e

    data = resp.json()
    pages = data['query']['pages']
    page = list(pages.values())[0]
    wikitext = page['revisions'][0]['slots']['main']['*']

    parsed = mwparserfromhell.parse(wikitext)
    unique = set()
    titles = []
    for link in parsed.filter_wikilinks():
      title = link.strip('[]').replace(' ', '_')
      if title not in unique:
        titles.append(title)
        unique.add(title)

    return '\n'.join(titles).encode('utf-8')

  def validate(self, **params):
    if 'url' not in params:
      return ('', '', ['Missing URL parameter'])

    if 'project' not in params:
      return ('', params['url'], ['Missing project parameter'])

    url = params['url']

    if params['project'] not in url:
      parsed_url = urllib.parse.urlparse(url)
      return ('', url, [
          'The domain of your URL does not match your '
          'selected project (project is: %s, URL has: %s)' %
          (params['project'], parsed_url.netloc)
      ])

    if not validators.url(url):
      return ('', url, ['That doesn\'t look like a valid URL.'])

    if 'wiki/' not in url:
      return ('', url, ['Valid book urls include /wiki/.'])

    return ('', '', [])
