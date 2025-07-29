import logging
import urllib.parse
from datetime import datetime

import regex
import requests

import wp1.logic.builder as logic_builder
import wp1.logic.selection as logic_selection
from wp1.constants import WP1_USER_AGENT
from wp1.credentials import CREDENTIALS, ENV
from wp1.exceptions import (
    InvalidZimDescriptionError,
    InvalidZimLongDescriptionError,
    InvalidZimTitleError,
    ObjectNotFoundError,
    ZimFarmError,
    ZimFarmTooManyArticlesError,
)
from wp1.logic import util
from wp1.models.wp10.selection import Selection
from wp1.models.wp10.builder import Builder
from wp1.time import get_current_datetime

REDIS_AUTH_KEY = 'zimfarm.auth'

# ZIM metadata limits as per https://wiki.openzim.org/wiki/Metadata
ZIM_TITLE_MAX_LENGTH = 30
ZIM_DESCRIPTION_MAX_LENGTH = 80
ZIM_LONG_DESCRIPTION_MAX_LENGTH = 4000

logger = logging.getLogger(__name__)

# The maximum number of articles that a Selection can contain if the user
# wishes to create a ZIM file for it. For Selections with more than this
# number, we perform validation in the frontend, as well as the API layer.
MAX_ZIMFARM_ARTICLE_COUNT = 50_000


def store_zimfarm_token(redis, data):
  redis.hset(REDIS_AUTH_KEY, mapping=data)


def request_zimfarm_token(redis):
  user = CREDENTIALS[ENV].get('ZIMFARM', {}).get('user')
  password = CREDENTIALS[ENV].get('ZIMFARM', {}).get('password')

  if user is None or password is None:
    raise ZimFarmError('Could not log into zimfarm, user/password not found in '
                       'site credentials')

  logger.debug('Requesting auth token from %s with username/password',
               get_zimfarm_url())
  r = requests.post('%s/auth/authorize' % get_zimfarm_url(),
                    headers={'User-Agent': WP1_USER_AGENT},
                    data={
                        'username': user,
                        'password': password
                    })
  try:
    r.raise_for_status()
  except requests.exceptions.HTTPError as e:
    logger.exception(r.text)
    raise ZimFarmError('Error getting authentication token for Zimfarm') from e

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
  try:
    r.raise_for_status()
  except requests.exceptions.HTTPError as e:
    logger.exception(r.text)
    raise ZimFarmError('Error getting authentication token for Zimfarm') from e

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


def get_webhook_url():
  token = CREDENTIALS[ENV].get('ZIMFARM', {}).get('hook_token')
  if token is None:
    return None

  base_url = CREDENTIALS[ENV].get('CLIENT_URL', {}).get('api')
  if base_url is None:
    return None

  return '%s/v1/builders/zim/status?token=%s' % (base_url,
                                                 urllib.parse.quote(token))


def nb_grapheme_for(value: str) -> int:
  """Number of graphemes (visually perceived characters) in a given string"""
  return len(regex.findall(r"\X", value))


def _validate_zim_metadata(title=None, description=None, long_description=None):
  """Validate ZIM metadata fields against length limits."""
  if title is not None and nb_grapheme_for(title) > ZIM_TITLE_MAX_LENGTH:
    raise InvalidZimTitleError(
        f"Title exceeds maximum length: {ZIM_TITLE_MAX_LENGTH} graphemes.")

  if description is not None and nb_grapheme_for(
      description) > ZIM_DESCRIPTION_MAX_LENGTH:
    raise InvalidZimDescriptionError(
        f"Description exceeds maximum length: {ZIM_DESCRIPTION_MAX_LENGTH} graphemes."
    )

  if long_description is not None and nb_grapheme_for(
      long_description) > ZIM_LONG_DESCRIPTION_MAX_LENGTH:
    raise InvalidZimLongDescriptionError(
        f"Long description exceeds maximum length: {ZIM_LONG_DESCRIPTION_MAX_LENGTH} graphemes."
    )

  if long_description is not None and nb_grapheme_for(
      long_description) < nb_grapheme_for(description):
    raise InvalidZimLongDescriptionError(
        f"Long description must be longer than the description.")

  if long_description is not None and long_description == description:
    raise InvalidZimLongDescriptionError(
        f"Long description must be different from the description.")


def get_zimfarm_schedule_name(builder_id: str) -> str:
    """Generate a unique schedule name for the ZIM file based on builder"""
    if not builder_id:
        raise ValueError('Builder ID cannot be None')
    parts = builder_id.split('-')
    # Use last two parts of the UUIDv4 for more uniqueness
    short_id = ''.join(parts[-2:])
    return f'wp1_selection_{short_id}'


def get_zim_filename_prefix(builder: Builder, selection: Selection) -> str:
  """Generate a filename prefix for the ZIM file based on builder and selection."""
  if builder is None or selection is None:
    raise ValueError(f"Given builder or selection was None")

  selection_id_frag = selection.s_id.decode('utf-8').split('-')[-1]
  builder_name = builder.b_name.decode('utf-8')
  return f"{util.safe_name(builder_name)}-{selection_id_frag}"


def _get_params(builder: Builder,
                selection: Selection,
                title: str = '',
                description: str = '',
                long_description: str = '') -> dict:
  if builder is None:
    raise ValueError('Given builder was None: %r' % builder)

  project = builder.b_project.decode('utf-8')

  image = CREDENTIALS[ENV].get('ZIMFARM', {}).get('image')
  if image is None:
    image = 'ghcr.io/openzim/mwoffliner:latest'
    logger.warning(
        'No ZIMFARM["image"] found in credentials, using latest (%s)', image)
  image_name, image_tag = image.split(':')

  config = {
      'task_name': 'mwoffliner',
      'warehouse_path': '/wikipedia',
      'image': {
          'name': image_name,
          'tag': image_tag,
      },
      'resources': logic_selection.get_resource_profile(selection),
      'platform': 'wikimedia',
      'monitor': False,
      'flags': {
          'mwUrl':
              'https://%s/' % project,
          'adminEmail':
              'contact+wp1@kiwix.org',
          'forceRender':
              'ActionParse',
          'articleList':
              logic_builder.latest_url_for(builder.b_id.decode('utf-8'), selection.s_content_type.decode('utf-8')),
          'customZimTitle':
              title,
          'customZimDescription':
              description,
          'customZimLongDescription':
              long_description if long_description else
              f"ZIM file created from a WP1 Selection. {description}",
          'filenamePrefix':
              get_zim_filename_prefix(builder, selection),
      }
  }
  cache_url = CREDENTIALS[ENV].get('ZIMFARM', {}).get('cache_url')
  if cache_url is not None:
    config['flags']['optimisationCacheUrl'] = cache_url
  else:
    logger.warning('No cache_url found in credentials, skipping '
                   'optimisationCacheUrl URL for zimfarm request')

  webhook_url = get_webhook_url()

  return {
      'name': get_zimfarm_schedule_name(builder.b_id.decode('utf-8')),
      'language': {
          'code': 'eng',
          'name_en': 'English',
          'name_native': 'English'
      },
      'category': 'wikipedia',
      'periodicity': 'manually',
      'tags': [],
      'enabled': True,
      'notification': {
          'ended': {
              'webhook': [webhook_url],
          },
      },
      'config': config,
  }


def _get_zimfarm_headers(token):
  return {"Authorization": "Token %s" % token, 'User-Agent': WP1_USER_AGENT}


def create_zimfarm_schedule(redis,
                            wp10db,
                            builder,
                            title='',
                            description='',
                            long_description=None):
  """
  Requests a ZIM file schedule from the Zimfarm for the given builder.
  """
  token = get_zimfarm_token(redis)
  if token is None:
    raise ZimFarmError('Error retrieving auth token for request')

  if builder is None:
    raise ObjectNotFoundError('Cannot schedule for None builder')

  _validate_zim_metadata(title, description, long_description)

  selection = logic_builder.latest_selection_for(wp10db, builder.b_id,
                                                 'text/tab-separated-values')
  article_count = selection.s_article_count
  if article_count is None or article_count > MAX_ZIMFARM_ARTICLE_COUNT:
    raise ZimFarmTooManyArticlesError(
        'Cannot create ZIM file for selection with %s articles, max is %s' %
        (article_count if article_count is not None else 'UNKNOWN number of',
         MAX_ZIMFARM_ARTICLE_COUNT))

  params = _get_params(builder,
                       selection,
                       title=title,
                       description=description,
                       long_description=long_description)
  base_url = get_zimfarm_url()
  headers = _get_zimfarm_headers(token)

  builder_id = builder.b_id.decode('utf-8')
  logger.info('Creating zimfarm schedule for ZIM for builder id=%s', builder_id)
  r = requests.post('%s/schedules/' % base_url, headers=headers, json=params)

  try:
    r.raise_for_status()
  except requests.exceptions.HTTPError as e:
    logger.exception(r.text)
    raise ZimFarmError('Error creating schedule for ZIM file creation') from e


def request_zimfarm_task(redis,
                         wp10db,
                         builder):
  """
  Requests a ZIM file task from the Zimfarm for the given builder.
  """
  token = get_zimfarm_token(redis)
  if token is None:
    raise ZimFarmError('Error retrieving auth token for request')

  if builder is None:
    raise ObjectNotFoundError('Cannot schedule for None builder')

  selection = logic_builder.latest_selection_for(wp10db, builder.b_id,
                                                 'text/tab-separated-values')
  article_count = selection.s_article_count
  if article_count is None or article_count > MAX_ZIMFARM_ARTICLE_COUNT:
    raise ZimFarmTooManyArticlesError(
        'Cannot create ZIM file for selection with %s articles, max is %s' %
        (article_count if article_count is not None else 'UNKNOWN number of',
         MAX_ZIMFARM_ARTICLE_COUNT))

  base_url = get_zimfarm_url()
  headers = _get_zimfarm_headers(token)

  logger.info('Creating ZIM task for builder id=%s', builder.b_id.decode('utf-8'))
  r = requests.post('%s/requested-tasks/' % base_url,
                    headers=headers,
                    json={'schedule_names': [get_zimfarm_schedule_name(builder.b_id.decode('utf-8')),]})

  try:
    r.raise_for_status()

    data = r.json()
    requested = data.get('requested')
    task_id = requested[0] if requested else None
    logger.info('Found task id=%s for builder id=%s', task_id, builder.b_id.decode('utf-8'))

    if task_id is None:
      raise ZimFarmError('Did not get scheduled task id')
  except requests.exceptions.HTTPError as e:
    logger.exception(r.text)
    raise ZimFarmError('Error requesting task for ZIM file creation') from e

  return task_id


def _get_task_by_id(task_id):
  if isinstance(task_id, bytes):
    task_id = task_id.decode('utf-8')
  base_url = get_zimfarm_url()

  r = requests.get('%s/tasks/%s' % (base_url, task_id))
  try:
    r.raise_for_status()
  except requests.exceptions.HTTPError:
    logger.exception(r.text)
    return None

  return r.json()


def is_zim_file_ready(task_id):
  data = _get_task_by_id(task_id)
  if data is None:
    # Some kind of HTTP error (could be 404 if the task hasn't moved
    # from requested-tasks to tasks yet). Ignore and we'll retry.
    return 'REQUESTED'

  if data.get('status') == 'failed':
    return 'FAILED'

  files = data.get('files', {})

  for key, value in files.items():
    if value.get('status') == 'uploaded':
      return 'FILE_READY'
  return 'REQUESTED'


def zim_file_url_for_task_id(task_id):
  data = _get_task_by_id(task_id)

  if data is None:
    return None

  files = data.get('files', {})
  name = None
  for _, value in files.items():
    name = value.get('name')
    break

  if name is None:
    raise ZimFarmError('Could not find filename for ZIM file, task_id = %s' %
                       task_id)

  warehouse_path = data.get('config', {}).get('warehouse_path')
  if warehouse_path is None:
    raise ZimFarmError(
        'Could not get warehouse path for ZIM file, task_id = %s' % task_id)

  base_url = CREDENTIALS[ENV].get('ZIMFARM', {}).get('s3_url')
  if base_url is None:
    raise ZimFarmError(
        'Configuration error, could not find ZIMFARM["s3_url"] in credentials')

  return f'{base_url}{warehouse_path}/{name}'


def cancel_zim_by_task_id(redis, task_id):
  if isinstance(task_id, bytes):
    task_id = task_id.decode('utf-8')

  token = get_zimfarm_token(redis)
  if token is None:
    raise ZimFarmError('Error retrieving auth token for request')
  base_url = get_zimfarm_url()
  headers = _get_zimfarm_headers(token)

  logger.info('Deleting requested task_id=%s', task_id)
  r = requests.delete('%s/requested-tasks/%s' % (base_url, task_id),
                      headers=headers)

  try:
    r.raise_for_status()
    return
  except requests.exceptions.HTTPError as e:
    if r.status_code != 404:
      raise ZimFarmError('Error attempting to delete requested task id=%s' %
                         task_id) from e

  logger.info('Task was no longer requested, cancelling (task_id=%s)', task_id)
  r = requests.post('%s/tasks/%s/cancel' % (base_url, task_id), headers=headers)

  try:
    r.raise_for_status()
  except requests.exceptions.HTTPError as e:
    raise ZimFarmError('Task could not be deleted/canceled (task_id=%s)' %
                       task_id)
    r.raise_for_status()
  except requests.exceptions.HTTPError as e:
    raise ZimFarmError('Task could not be deleted/canceled (task_id=%s)' %
                       task_id)
