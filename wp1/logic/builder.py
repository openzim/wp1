import json
import logging

import attr

from wp1.constants import CONTENT_TYPE_TO_EXT, EXT_TO_CONTENT_TYPE
from wp1.credentials import CREDENTIALS, ENV
from wp1.exceptions import ObjectNotFoundError, UserNotAuthorizedError
import wp1.logic.selection as logic_selection
import wp1.logic.util as logic_util
from wp1.models.wp10.builder import Builder
from wp1.models.wp10.selection import Selection
from wp1 import queues
from wp1.redis_db import connect as redis_connect
from wp1.storage import connect_storage
from wp1.wp10_db import connect as wp10_connect
from wp1 import zimfarm

logger = logging.getLogger(__name__)


def create_or_update_builder(wp10db,
                             name,
                             user_id,
                             project,
                             params,
                             model,
                             builder_id=None):
  params = json.dumps(params).encode('utf-8')
  builder = Builder(b_name=name,
                    b_user_id=user_id,
                    b_model=model,
                    b_project=project,
                    b_params=params)
  builder.set_updated_at_now()
  if builder_id is None:
    builder.set_created_at_now()
    return insert_builder(wp10db, builder)

  if isinstance(builder_id, bytes):
    builder.b_id = builder_id
  elif isinstance(builder_id, str):
    builder.b_id = builder_id.encode('utf-8')
  else:
    builder.b_id = str(builder_id).encode('utf-8')
  if update_builder(wp10db, builder):
    return builder_id

  return None


def insert_builder(wp10db, builder):
  builder.set_id()
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''INSERT INTO builders
             (b_id, b_name, b_user_id, b_project, b_params, b_model, b_created_at, b_updated_at)
           VALUES
             (%(b_id)s, %(b_name)s, %(b_user_id)s, %(b_project)s, %(b_params)s, %(b_model)s,
              %(b_created_at)s, %(b_updated_at)s)
        ''', attr.asdict(builder))
  wp10db.commit()
  return builder.b_id


def update_current_version(wp10db, builder, version):
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''UPDATE builders
           SET b_current_version=%(version)s
           WHERE b_id = %(b_id)s AND b_user_id = %(b_user_id)s
        ''', {
            'version': version,
            'b_id': builder.b_id,
            'b_user_id': builder.b_user_id
        })
    rowcount = cursor.rowcount
  wp10db.commit()
  return rowcount > 0


def update_builder(wp10db, builder):
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''UPDATE builders
          SET b_name = %(b_name)s, b_project = %(b_project)s, b_params = %(b_params)s,
              b_model = %(b_model)s, b_updated_at = %(b_updated_at)s
          WHERE b_id = %(b_id)s AND b_user_id = %(b_user_id)s
        ''', attr.asdict(builder))
    rowcount = cursor.rowcount
  wp10db.commit()
  return rowcount > 0


def delete_builder(wp10db, user_id, builder_id):
  if not isinstance(builder_id, bytes):
    builder_id = str(builder_id).encode('utf-8')

  with wp10db.cursor() as cursor:
    cursor.execute(
        '''SELECT s.s_object_key as object_key FROM selections AS s
           JOIN builders AS b ON b.b_id = s.s_builder_id
           WHERE b.b_user_id = %s AND b.b_id = %s
             AND s.s_object_key IS NOT NULL
        ''', (user_id, builder_id))
    keys_to_delete = [d['object_key'] for d in cursor.fetchall()]
    cursor.execute(
        '''DELETE b, s FROM builders AS b
           LEFT JOIN selections AS s ON s.s_builder_id = b.b_id
           WHERE b.b_user_id = %s AND b.b_id = %s
        ''', (user_id, builder_id))
    rowcount = cursor.rowcount

  # Delete the object keys from the s3-like backend
  s3_success = logic_selection.delete_keys_from_storage(keys_to_delete)

  wp10db.commit()
  return {
      'db_delete_success': rowcount > 0,
      's3_delete_success': s3_success,
  }


def get_builder(wp10db, id_):
  with wp10db.cursor() as cursor:
    cursor.execute('SELECT * FROM builders WHERE b_id = %s', id_)
    db_builder = cursor.fetchone()
    return Builder(**db_builder) if db_builder else None


def materialize_builder(builder_cls, builder_id, content_type):
  wp10db = wp10_connect()
  s3 = connect_storage()
  logging.basicConfig(level=logging.INFO)

  try:
    builder = get_builder(wp10db, builder_id)
    materializer = builder_cls()
    logger.info('Materializing builder id=%s, content_type=%s with class=%s' %
                (builder_id, content_type, builder_cls))
    materializer.materialize(s3, wp10db, builder, content_type)
  finally:
    wp10db.close()


def latest_url_for(builder_id, content_type):
  """Returns the redirect URL for the latest selection for a builder.

  This is the URL on this API server that redirects to S3-storage.
  """
  ext = CONTENT_TYPE_TO_EXT.get(content_type)
  if ext is None:
    logger.warning(
        'Attempt to get latest selection URL with unrecognized content type: %r',
        content_type)
    return None
  server_url = CREDENTIALS.get(ENV, {}).get('CLIENT_URL', {}).get('api')
  if server_url is None:
    logger.warning('Could not determine server API URL. Check credentials.py')
    return None
  return '%s/v1/builders/%s/selection/latest.%s' % (server_url, builder_id, ext)


def latest_zim_for(builder_id):
  """Returns the redirect URL for the latest ZIM file for a builder."""
  server_url = CREDENTIALS.get(ENV, {}).get('CLIENT_URL', {}).get('api')
  if server_url is None:
    logger.warning('Could not determine server API URL. Check credentials.py')
    return None
  return '%s/v1/builders/%s/zim/latest' % (server_url, builder_id)


def latest_selection_for(wp10db, builder_id, content_type):
  """Returns the latest Selection with the given content type for a builder.

  Returns the value as a Selection model.
  """
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''SELECT s.*
           FROM selections AS s JOIN builders as b
             ON s.s_builder_id = b.b_id
             AND s.s_version = b.b_current_version
           WHERE s.s_content_type = %s AND b.b_id = %s
        ''', (content_type, builder_id))
    db_selection = cursor.fetchone()
  if db_selection is None:
    logger.warning(
        'Could not find latest selection for builder id=%s, content_type=%s',
        builder_id, content_type)
    return None

  return Selection(**db_selection)


def latest_selection_url(wp10db, builder_id, ext):
  """Returns the raw S3-like storage URL for the latest selection for the given builder.

  This is in contrast with latest_url_for, which returns the redirect URL on this API
  server for a selection. This function is used when resolving the redirect, to return
  the actual URL.
  """
  content_type = EXT_TO_CONTENT_TYPE.get(ext)
  if content_type is None:
    logger.warning(
        'Attempt to get latest selection with unrecognized extension: %r', ext)
    return None

  selection = latest_selection_for(wp10db, builder_id, content_type)
  if selection is None:
    return None

  if selection.s_object_key is None:
    logger.warning('Object key for selection was None, builder id=%s',
                   builder_id)
    return None

  return logic_selection.url_for(selection.s_object_key.decode('utf-8'))


def latest_zim_file_url_for(wp10db, builder_id):
  selection = latest_selection_for(wp10db, builder_id,
                                   'text/tab-separated-values')
  if selection is None:
    return None

  if selection.s_zimfarm_status != b'FILE_READY':
    logger.warning('Attempt to get ZIM URL before file ready, builder id=%s',
                   builder_id)
    return None

  return logic_selection.zim_file_url_for_selection(selection)


def latest_selections_with_errors(wp10db, builder_id):
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''SELECT s.s_status, s.s_error_messages, s.s_content_type
           FROM selections AS s JOIN builders as b
             ON s.s_builder_id = b.b_id
             AND s.s_version = b.b_current_version
           WHERE b.b_id = %s AND s.s_status IS NOT NULL AND s.s_status != 'OK'
        ''', (builder_id,))
    data = cursor.fetchall()

  res = []
  for db_selection in data:
    status = {
        'status':
            db_selection['s_status'].decode('utf-8'),
        'ext':
            CONTENT_TYPE_TO_EXT.get(
                db_selection['s_content_type'].decode('utf-8'), '???')
    }
    if 's_error_messages' in db_selection and db_selection['s_error_messages']:
      try:
        error_messages = json.loads(
            db_selection['s_error_messages'].decode('utf-8'))
      except json.decoder.JSONDecodeError:
        error_messages = {'error_messages': []}
      status.update(**error_messages)
    res.append(status)

  return res


def schedule_zim_file(redis,
                      wp10db,
                      user_id,
                      builder_id,
                      description='',
                      long_description=''):
  if isinstance(builder_id, str):
    builder_id = builder_id.encode('utf-8')
  builder = get_builder(wp10db, builder_id)
  if builder is None:
    raise ObjectNotFoundError('Could not find builder with id = %s' %
                              builder_id)

  if builder.b_user_id != user_id:
    raise UserNotAuthorizedError(
        'Could not use builder id = %s for user id = %s' %
        (builder_id, user_id))

  task_id = zimfarm.schedule_zim_file(redis,
                                      wp10db,
                                      builder,
                                      description=description,
                                      long_description=long_description)
  selection = latest_selection_for(wp10db, builder_id,
                                   'text/tab-separated-values')

  with wp10db.cursor() as cursor:
    cursor.execute(
        '''UPDATE selections SET
             s_zimfarm_status = 'REQUESTED', s_zimfarm_task_id = %s,
             s_zimfarm_error_messages = NULL
           WHERE s_id = %s
        ''', (task_id, selection.s_id))
  wp10db.commit()

  return task_id


def latest_zimfarm_status(wp10db, builder_id):
  selection = latest_selection_for(wp10db, builder_id,
                                   'text/tab-separated-values')
  return selection.s_zimfarm_status.decode('utf-8')


def on_zim_file_status_poll(task_id):
  wp10db = wp10_connect()
  redis = redis_connect()

  if zimfarm.is_zim_file_ready(task_id):
    logic_selection.update_zimfarm_task(wp10db,
                                        task_id,
                                        'FILE_READY',
                                        set_updated_now=True)
  else:
    queues.poll_for_zim_file_status(redis, task_id)

  wp10db.close()


def _get_builder_data(b):
  return {
      'id': b['b_id'].decode('utf-8'),
      'name': b['b_name'].decode('utf-8'),
      'project': b['b_project'].decode('utf-8'),
      'model': b['b_model'].decode('utf-8'),
      'created_at': logic_util.wp10_timestamp_to_unix(b['b_created_at']),
      'updated_at': logic_util.wp10_timestamp_to_unix(b['b_updated_at']),
  }


def _get_selection_data(b):
  data = {
      's_id': None,
      's_updated_at': None,
      's_content_type': None,
      's_extension': None,
      's_url': None,
      's_status': None,
      's_zimfarm_status': None,
      's_zim_file_updated_at': None,
      's_zim_file_url': None,
  }

  has_selection = b['s_id'] is not None
  has_status = b['s_status'] is not None
  is_ok_status = b['s_status'] == b'OK'
  is_zim_ready = b['s_zimfarm_status'] == b'FILE_READY'

  if has_selection:
    content_type = b['s_content_type'].decode('utf-8')
    data['s_id'] = b['s_id'].decode('utf-8')
    data['s_updated_at'] = logic_util.wp10_timestamp_to_unix(b['s_updated_at'])
    data['s_content_type'] = content_type
    data['s_extension'] = CONTENT_TYPE_TO_EXT.get(content_type, '???')
    data['s_zimfarm_status'] = b['s_zimfarm_status'].decode('utf-8')
    if has_status:
      data['s_status'] = b['s_status'].decode('utf-8')

    if is_ok_status or not has_status:
      data['s_url'] = latest_url_for(b['b_id'].decode('utf-8'), content_type)

    if b['s_zim_file_updated_at'] is not None:
      data['s_zim_file_updated_at'] = logic_util.wp10_timestamp_to_unix(
          b['s_zim_file_updated_at'])

    if content_type == 'text/tab-separated-values' and is_zim_ready:
      data['s_zim_file_url'] = latest_zim_for(b['b_id'].decode('utf-8'))

  return data


def get_builders_with_selections(wp10db, user_id):
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''SELECT * FROM selections
           RIGHT JOIN builders
             ON selections.s_builder_id = builders.b_id
             AND selections.s_version = builders.b_current_version
           WHERE b_user_id = %(b_user_id)s
           ORDER BY builders.b_updated_at DESC
        ''', {'b_user_id': user_id})
    data = cursor.fetchall()

  builders = {}
  result = []
  for b in data:
    builder = {}
    builder.update(_get_builder_data(b))
    builder.update(_get_selection_data(b))
    result.append(builder)

  return result
