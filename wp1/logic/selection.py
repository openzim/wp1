import html
import json
import logging
import urllib.parse

import attr

from wp1.constants import CONTENT_TYPE_TO_EXT, TS_FORMAT_WP10, ZIM_FILE_TTL
from wp1.models.wp10.selection import Selection
from wp1.models.wp10.zim_file import ZimFile
from wp1.storage import connect_storage
from wp1.logic import util
from wp1.timestamp import utcnow
from wp1 import zimfarm

try:
  from wp1.credentials import ENV, CREDENTIALS
  S3_PUBLIC_URL = CREDENTIALS.get(ENV, {}).get('CLIENT_URL', {}).get(
      's3', 'http://credentials.not.found.fake')
except ImportError:
  S3_PUBLIC_URL = 'http://credentials.not.found.fake'

DEFAULT_SELECTION_NAME = 'selection'

logger = logging.getLogger(__name__)


def insert_selection(wp10db, selection):
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''INSERT INTO selections
             (s_id, s_builder_id, s_version, s_content_type, s_updated_at,
              s_object_key, s_status, s_error_messages)
             VALUES
             (%(s_id)s, %(s_builder_id)s, %(s_version)s, %(s_content_type)s,
              %(s_updated_at)s, %(s_object_key)s, %(s_status)s, %(s_error_messages)s)
    ''', attr.asdict(selection))
    cursor.execute(
        'INSERT INTO zim_files (z_selection_id, z_status)'
        ' VALUES (%s, "NOT_REQUESTED")', (selection.s_id,))
  wp10db.commit()


def get_next_version(wp10db, builder_id, content_type):
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''SELECT MAX(s_version) as version FROM selections
      WHERE s_builder_id = %s AND s_content_type = %s
      ''', (builder_id, content_type))
    data = cursor.fetchall()
  version = data[0]['version']
  if version is None:
    return 1
  else:
    return version + 1


def url_for_selection(selection):
  if not selection:
    raise ValueError('Cannot get url for empty selection')
  return url_for(selection.s_object_key)


def url_for(object_key):
  if not object_key:
    raise ValueError('Cannot get url for empty object_key')
  path = urllib.parse.quote(
      object_key if isinstance(object_key, str) else object_key.decode('utf-8'))
  return '%s/%s' % (S3_PUBLIC_URL, path)


def zim_file_requested_at_for(wp10db, task_id):
  with wp10db.cursor() as cursor:
    cursor.execute(
        'SELECT z_requested_at '
        'FROM zim_files WHERE z_task_id = %s', task_id)
    data = cursor.fetchone()
    if data is None or data['z_requested_at'] is None:
      return None

  return util.wp10_timestamp_to_unix(data['z_requested_at'])


def object_key_for(selection_id,
                   content_type,
                   model,
                   name=None,
                   use_legacy_schema=False):
  if not selection_id:
    raise ValueError('Cannot get object key for empty selection_id')
  if not model:
    raise ValueError('Expected WP1 model name, got: %r' % model)
  if name is None:
    name = DEFAULT_SELECTION_NAME
  ext = CONTENT_TYPE_TO_EXT.get(content_type, '???')
  if use_legacy_schema:
    return 'selections/%(model)s/%(id)s.%(ext)s' % {
        'model': model,
        'id': selection_id,
        'ext': ext,
    }

  return 'selections/%(model)s/%(id)s/%(name)s.%(ext)s' % {
      'model': model,
      'id': selection_id,
      'ext': ext,
      'name': util.safe_name(name),
  }


def object_key_for_selection(selection,
                             model,
                             name=None,
                             use_legacy_schema=False):
  if not selection:
    raise ValueError('Cannot get object key for empty selection')
  return object_key_for(selection.s_id.decode('utf-8'),
                        selection.s_content_type.decode('utf-8'),
                        model,
                        name=name,
                        use_legacy_schema=use_legacy_schema)


def delete_keys_from_storage(keys):
  if isinstance(keys, (bytes)):
    keys = [keys]

  for key in keys:
    if isinstance(key, str):
      raise ValueError('Expected keys to all be bytes, not str')

  s3 = connect_storage()
  resp = s3.bucket.delete_objects(
      Delete={
          'Objects': [{
              'Key': html.escape(k.decode('utf-8'))
          } for k in keys],
          'Quiet': True,
      })

  fully_successful = True

  # TODO: Check for errors in the response. For now, just pretend
  # it's always successful.
  # for e in (resp if resp is not None else {}).get('Errors', []):
  #   fully_successful = False
  #   logger.warning('Error deleting %r: [code=%r, msg=%r]',
  #                  (e['Key'], e['Code'], e['Message']))

  return fully_successful


def set_error_messages(selection, e):
  messages = [str(e)]
  # Use __cause__ because we can use '... from e' expressions to either set or suppress the cause.
  if e.__cause__:
    messages.append(str(e.__cause__))
  selection.s_error_messages = json.dumps({'error_messages': messages})


def update_zimfarm_task(wp10db, task_id, status, set_updated_now=False):
  with wp10db.cursor() as cursor:
    if set_updated_now:
      updated_at = utcnow().strftime(TS_FORMAT_WP10).encode('utf-8')
      with wp10db.cursor() as cursor:
        cursor.execute(
            '''UPDATE zim_files SET z_status = %s, z_updated_at = %s
               WHERE z_task_id = %s''', (status, updated_at, task_id))
        found = bool(cursor.rowcount)
    else:
      cursor.execute('UPDATE zim_files SET z_status = %s WHERE z_task_id = %s',
                     (status, task_id))
      found = bool(cursor.rowcount)
  wp10db.commit()
  return found


def is_zim_file_deleted(update_at_timestamp):
  return utcnow().timestamp() - update_at_timestamp > ZIM_FILE_TTL


TASK_CPU = 3
TASK_MEMORY = 1024 * 1024 * 1024 * 3  # Base memory is 3 GB
TASK_DISK = 1024 * 1024 * 1024 * 20  # Base disk space is 20 GB


def get_resource_profile(s3, selection):
  data = s3.client.head_object(Bucket=s3.bucket_name,
                               Key=selection.s_object_key.decode('utf-8'))
  length = data.get('ContentLength', 1024)
  article_estimate = length / 15  # Assume each article name is 15 chars long.
  multiplier = (
      (article_estimate // 1000000) + 1)  # 1 multiplier for every 1M articles
  return {
      'cpu': TASK_CPU,
      # 3 GB of memory for each 1M articles
      'memory': int(TASK_MEMORY * multiplier),
      # 20 GB of disk for each 1M articles
      'disk': int(TASK_DISK * multiplier),
  }
