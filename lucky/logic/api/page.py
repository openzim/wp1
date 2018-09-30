from datetime import datetime
import logging
import time

from api import site
import logic.util as logic_util

logger = logging.getLogger(__name__)

def get_redirect(title_with_ns):
  logger.info('Querying api for redirects for %s', title_with_ns)
  res = site.api(
    'query', titles=title_with_ns, redirects=1, prop='revisions', rvlimit=1)

  if 'query' not in res or 'redirects' not in res['query']:
    return None
  redir = res['query']['redirects'][0]['to']
  if len(redir) == 0:
    return None

  key = next(iter(res['query']['pages']))
  page = res['query']['pages'][key]
  return {
    'ns': page['ns'],
    'title': page['title'],
    'timestamp': datetime.strptime(
      page['revisions'][0]['timestamp'], '%Y-%m-%dT%H:%M:%SZ'),
  }

def get_moves(title_with_ns):
  logger.info('Querying api for moves of page %s', title_with_ns)
  res = site.logevents(title=title_with_ns, type='move')

  ans = []
  for event in res:
    print(repr(event))
    if 'params' not in event:
      continue
    ans.append({
      'ns': event['params']['target_ns'],
      'title': event['params']['target_title'],
      'timestamp': datetime.fromtimestamp(time.mktime(event['timestamp'])),
    })

  return ans or None
