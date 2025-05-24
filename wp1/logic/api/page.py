import logging
import re
import time
from datetime import datetime

import wp1.logic.util as logic_util
from wp1.api import login as site_login
from wp1.api import site
from wp1.constants import TS_FORMAT

logger = logging.getLogger(__name__)
RE_NAMESPACE = re.compile(r'^([^:]+:)')


def get_redirect(title_with_ns):
  logger.debug('Querying api for redirects for %s', title_with_ns)
  site_login()
  if site is None or not site.logged_in:
    return None

  res = None
  retries = 3
  while retries:
    try:
      res = site.api('query',
                     titles=title_with_ns,
                     redirects=1,
                     prop='revisions',
                     rvlimit=1)
      break
    except:
      logger.exception('Error contacting API for redirects, retrying...')
      retries -= 1

  if res is None:
    logger.warning('Error contacting API, returning None')
    return None

  if ('query' not in res or 'redirects' not in res['query'] or
      len(res['query']['redirects'][0]['to']) == 0):
    return None

  key = next(iter(res['query']['pages']))
  page = res['query']['pages'][key]
  return {
      'ns':
          page['ns'],
      'title':
          page['title'].replace(' ', '_'),
      'timestamp_dt':
          datetime.strptime(page['revisions'][0]['timestamp'], TS_FORMAT),
  }


def get_moves(title_with_ns):
  logger.debug('Querying api for moves of page %s', title_with_ns)
  site_login()
  if site is None or not site.logged_in:
    return None

  res = None
  retries = 3
  while retries:
    try:
      res = site.logevents(title=title_with_ns, type='move')
      break
    except:
      logger.exception('Error contacting API for moves, retrying...')
      retries -= 1

  if res is None:
    logger.warning('Error contacting API, returning None')
    return None

  ans = []
  retries = 3
  while retries:
    try:
      for event in res:
        if 'params' not in event:
          continue
        datapoint = {
            'ns':
                event['params']['target_ns'],
            'title':
                event['params']['target_title'].replace(' ', '_'),
            'timestamp_dt':
                datetime.fromtimestamp(time.mktime(event['timestamp'])),
        }
        if datapoint['ns'] != 0:
          datapoint['title'] = RE_NAMESPACE.sub('', datapoint['title'])
        ans.append(datapoint)
      break
    except:
      retries -= 1

  if retries == 0:
    logger.warning('Error contacting continuation API, returning None')

  return ans or None
  return ans or None
