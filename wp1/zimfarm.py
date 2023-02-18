from datetime import timedelta
from functools import wraps
import time

import requests

from wp1.constants import WP1_USER_AGENT
from wp1.credentials import CREDENTIALS, ENV
from wp1.logic import util
import wp1.logic.builder as logic_builder
import wp1.logic.selection as logic_selection
from wp1.timestamp import utcnow

TASK_CPU = 2
TASK_MEMORY = 1024
TASK_DISK = 2048
MWOFFLINER_IMAGE = 'ghcr.io/openzim/mwoffliner:1.12.1'


def _get_params(wp10db, builder_id):
  if isinstance(builder_id, str):
    builder_id = builder_id.encode('utf-8')

  builder = logic_builder.get_builder(wp10db, builder_id)
  project = builder.b_project.decode('utf-8')
  selection = logic_builder.latest_selection_for(wp10db, builder_id,
                                                 'text/tab-separated-values')

  config = {
      'task_name': 'zimit',
      'warehouse_path': '/wp1',
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

  return {
      'name': 'wp1_selection_%s' % selection.s_id.decode('utf-8'),
      'language': {
          'code': 'eng',
          'name_en': 'English',
          'name_native': 'English'
      },
      'category': 'other',
      'periodicity': 'manually',
      'tags': [],
      'enabled': True,
      'config': config,
  }


def store_zimfarm_token(wp10db, data):
  data['expires_at'] = utcnow() + timedelta(seconds=data['expires_in'])

  with wp10db.cursor() as cursor:
    cursor.execute(
        'INSERT INTO zimfarm_auth (access_token, expires_at, refresh_token) '
        'VALUES (%(access_token)s, %(expires_at)s, %(refresh_token)s)', data)


def request_zimfarm_token(wp10db):
  user = CREDENTIALS[ENV].get('ZIMFARM', {}).get('user')
  password = CREDENTIALS[ENV].get('ZIMFARM', {}).get('password')

  if user is None or password is None:
    raise ZimFarmError(
        'Could not log into zimfarm, user/password not found in credentials.py')

  r = requests.post('%s/auth/authorize' % get_zimfarm_url,
                    headers={'User-Agent': WP1_USER_AGENT},
                    data={
                        'username': user,
                        'password': password
                    })
  r.raise_for_status()

  data = r.json()
  print(data)

  store_zimfarm_token(wp10db, data)

  return data['access_token']


def refresh_zimfarm_token(wp10db, refresh_token):
  r = requests.post(
      '%s/auth/token',
      headers={
          'User-Agent': WP1_USER_AGENT,
          'refresh-token': refresh_token
      },
  )
  r.raise_for_status()

  data = r.json()
  print(data)

  store_zimfarm_token(wp10db, data)

  return data['access_token']


def get_zimfarm_token(wp10db):
  with wp10db.cursor() as cursor:
    cursor.execute(
        'SELECT access_token, expires_at, refresh_token FROM zimfarm_auth LIMIT 1'
    )
    data = cursor.fetchone()
    if data is None:
      return request_zimfarm_token(wp10db)

  if data['expires_at'] < time.mktime(utcnow().timetuple()):
    # Token is expired, refresh
    return refresh_zimfarm_token(wp10db, data['refresh_token'])

  return data['access_token']


def get_zimfarm_url():
  return CREDENTIALS[ENV].get('ZIMFARM', {}).get('url', '')


def schedule_zim_file(wp10db, builder_id):
  token = get_zimfarm_token(wp10db)

  params = _get_params(wp10db, builder_id)
  base_url = get_zimfarm_url()

  r = requests.post('%s/schedules/' % base_url,
                    headers={'User-Agent': WP1_USER_AGENT},
                    json=params)

  r.raise_for_status()

  r = requests.post('%s/requested_tasks/' % base_url,
                    headers={'User-Agent': WP1_USER_AGENT},
                    json={schedule_names: [params['name'],]})

  r.raise_for_status()

  task_id = r.json()['requested'][0]
  print(task_id)

  r = requets.delete('%s/schedules/%s' % (base_url, params['name']))
