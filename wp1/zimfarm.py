from datetime import datetime, timedelta
from functools import wraps
import logging
import time

import requests

from wp1.constants import WP1_USER_AGENT
from wp1.credentials import CREDENTIALS, ENV
from wp1.exceptions import ZimFarmError
from wp1.logic import util
import wp1.logic.builder as logic_builder
import wp1.logic.selection as logic_selection
from wp1.timestamp import utcnow
from wp1.time import get_current_datetime

TASK_CPU = 2
TASK_MEMORY = 1024 * 1024 * 1024
TASK_DISK = 2048 * 1024 * 100
MWOFFLINER_IMAGE = 'ghcr.io/openzim/mwoffliner:latest'
REDIS_AUTH_KEY = 'zimfarm.auth'

logger = logging.getLogger(__name__)


def store_zimfarm_token(redis, data):
  redis.hset(REDIS_AUTH_KEY, mapping=data)


def request_zimfarm_token(redis):
  user = CREDENTIALS[ENV].get('ZIMFARM', {}).get('user')
  password = CREDENTIALS[ENV].get('ZIMFARM', {}).get('password')

  if user is None or password is None:
    raise ZimFarmError(
        'Could not log into zimfarm, user/password not found in credentials.py')

  logger.debug('Requesting auth token from %s with username/password',
               get_zimfarm_url())
  r = requests.post('%s/auth/authorize' % get_zimfarm_url(),
                    headers={'User-Agent': WP1_USER_AGENT},
                    data={
                        'username': user,
                        'password': password
                    })
  r.raise_for_status()

  data = r.json()
  store_zimfarm_token(redis, data)

  access_token = data.get('access_token')
  if access_token is None:
    logger.warning('Access token from zimfarm API was None, full response: %s',
                   data)
  return access_token


def refresh_zimfarm_token(redis, refresh_token):
  logger.debug('Requesting access_token from %s using refresh_token',
               get_zimfarm_url())
  r = requests.post(
      '%s/auth/token' % get_zimfarm_url(),
      headers={
          'User-Agent': WP1_USER_AGENT,
          'refresh-token': refresh_token
      },
  )
  r.raise_for_status()

  data = r.json()
  access_token = data.get('access_token')
  if access_token is None:
    logger.warning('Access token from zimfarm API was None, full response: %s',
                   data)

  return access_token


def get_zimfarm_token(redis):
  data = redis.hgetall(REDIS_AUTH_KEY)
  if data is None or data.get('refresh_token') is None:
    logger.debug('No saved zimfarm refresh_token, requesting')
    return request_zimfarm_token(redis)

  access_expired = datetime.strptime(
      data.get('expires_in', '1970-01-01T00:00:00Z'),
      '%Y-%m-%dT%H:%M:%SZ') < get_current_datetime()

  if access_expired:
    logger.debug('Zimfarm access_token is expired, refreshing')
    return refresh_zimfarm_token(redis, data['refresh_token'])

  return data.get('access_token')


def get_zimfarm_url():
  url = CREDENTIALS[ENV].get('ZIMFARM', {}).get('url')
  if url is None:
    raise ZimFarmError(
        'CREDENTIALS did not contain ["ZIMFARM"]["url"], environment = %s' %
        ENV)
  return url


def _get_params(wp10db, builder_id):
  if isinstance(builder_id, str):
    builder_id = builder_id.encode('utf-8')

  builder = logic_builder.get_builder(wp10db, builder_id)
  project = builder.b_project.decode('utf-8')
  selection = logic_builder.latest_selection_for(wp10db, builder_id,
                                                 'text/tab-separated-values')

  config = {
      'task_name': 'mwoffliner',
      'warehouse_path': '/wikipedia',
      'image': {
          'name': MWOFFLINER_IMAGE.split(':')[0],
          'tag': MWOFFLINER_IMAGE.split(':')[1],
      },
      'resources': {
          'cpu': TASK_CPU,
          'memory': TASK_MEMORY,
          'disk': TASK_DISK,
      },
      'platform': None,
      'monitor': False,
      'flags': {
          'mwUrl': 'https://%s/' % project,
          'adminEmail': 'contact+wp1@kiwix.org',
          'articleList': logic_selection.url_for_selection(selection),
          'customZimTitle': util.safe_name(builder.b_name.decode('utf-8')),
      }
  }

  name = 'wp1_selection_%s' % selection.s_id.decode('utf-8').split('-')[-1]

  return {
      'name': name,
      'language': {
          'code': 'eng',
          'name_en': 'English',
          'name_native': 'English'
      },
      'category': 'wikipedia',
      'periodicity': 'manually',
      'tags': [],
      'enabled': True,
      'config': config,
  }


def _get_zimfarm_headers(token):
  return {"Authorization": "Token %s" % token, 'User-Agent': WP1_USER_AGENT}


def schedule_zim_file(redis, wp10db, builder_id):
  token = get_zimfarm_token(redis)
  if token is None:
    raise ZimfarmError('Could not retrieve auth token for request')

  params = _get_params(wp10db, builder_id)
  base_url = get_zimfarm_url()
  headers = _get_zimfarm_headers(token)

  r = requests.post('%s/schedules/' % base_url, headers=headers, json=params)

  try:
    r.raise_for_status()
  except Exception:
    logger.exception(r.text)
    raise

  r = requests.post('%s/requested-tasks/' % base_url,
                    headers=headers,
                    json={'schedule_names': [params['name'],]})

  try:
    r.raise_for_status()

    data = r.json()
    requested = data.get('requested')
    task_id = requested[0] if requested else None

    if task_id is None:
      raise ZimFarmError('Did not get scheduled task id')
  except Exception:
    logger.exception(r.text)
    raise
  finally:
    requests.delete('%s/schedules/%s' % (base_url, params['name']),
                    headers=headers)

  return task_id
