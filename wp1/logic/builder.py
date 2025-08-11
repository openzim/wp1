import importlib
import json
import logging

import attr

from kiwixstorage import KiwixStorage
from pymysql.connections import Connection
from redis import Redis

import wp1.logic.selection as logic_selection
import wp1.logic.zim_schedules as logic_zim_schedules
import wp1.logic.zim_files as logic_zim_tasks
import wp1.logic.util as logic_util
from wp1 import app_logging, queues, zimfarm
from wp1.constants import (CONTENT_TYPE_TO_EXT, EXT_TO_CONTENT_TYPE,
                           MAX_ZIM_FILE_POLL_TIME, TS_FORMAT_WP10)
from wp1.credentials import CREDENTIALS, ENV
from wp1.environment import Environment
from wp1.exceptions import (ObjectNotFoundError, UserNotAuthorizedError,
                            ZimFarmError)
from wp1.models.wp10.builder import Builder
from wp1.models.wp10.selection import Selection
from wp1.models.wp10.zim_file import ZimTask
from wp1.models.wp10.zim_schedule import ZimSchedule
from wp1.redis_db import connect as redis_connect
from wp1.storage import connect_storage
from wp1.timestamp import utcnow
from wp1.web import emails
from wp1.wp10_db import connect as wp10_connect

logger = logging.getLogger(__name__)


def get_builder_module_class(model: str):
  """Dynamically imports the builder module and returns the Builder class."""
  builder_module = importlib.import_module(model)
  builder_cls = getattr(builder_module, 'Builder')
  if builder_cls is None:
    logger.warning('Could not find model: %s', model)
    raise ImportError(f'Builder class not found in module {model}')
  return builder_cls

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
             (b_id, b_name, b_user_id, b_project, b_params, b_model,
              b_created_at, b_updated_at)
           VALUES
             (%(b_id)s, %(b_name)s, %(b_user_id)s, %(b_project)s,
              %(b_params)s, %(b_model)s, %(b_created_at)s,
              %(b_updated_at)s)
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
    if db_builder is None:
      raise ObjectNotFoundError(f'No builder with id={id_}')
    return Builder(**db_builder)


def materialize_builder(builder_cls,
                        builder: Builder,
                        content_type: str,
                        s3: KiwixStorage = None,
                        redis: Redis = None,
                        wp10db: Connection = None):
  """
  Materializes a builder selection using the given builder class and content type.
  This is intended to be used by worker processes.
  """
  should_close = False
  if wp10db is None:
    wp10db = wp10_connect()
    should_close = True
  if redis is None:
    redis = redis_connect()
  if s3 is None:
    s3 = connect_storage()
  app_logging.configure_logging()

  try:
    materializer = builder_cls()
    next_version = logic_selection.get_next_version(wp10db, builder.b_id, content_type)
    logger.info('Materializing builder id=%s, content_type=%s with class=%s',
        builder.b_id, content_type, materializer.__class__.__name__)
    materializer.materialize(s3, wp10db, builder, content_type, next_version)
    update_current_version(wp10db, builder, next_version)
    updated = maybe_update_selection_zim_version(wp10db, builder, next_version)
    if not updated:
      # The ZIM file was not updated, which means there's an existing ZIM
      # that's ready that needs to be replaced. Schedule the ZIM file to
      # be automatically created. We don't need to do this if the ZIM
      # version was updated, because that indicates that the ZIM file
      # was never requested or errored and should remain in that state.
      auto_handle_zim_generation(redis, wp10db, builder.b_id)
  finally:
    if should_close:
      wp10db.close()


def maybe_update_selection_zim_version(wp10db, builder, selection_version):
  current_zim = latest_zim_file_for(wp10db, builder.b_id)
  if current_zim is not None and current_zim.z_status == b'FILE_READY':
    # There is an existing ZIM that's ready. Leave it for now and
    # the version will get updated when the new ZIM is uploaded.
    return False

  with wp10db.cursor() as cursor:
    cursor.execute(
        'UPDATE builders b SET b.b_selection_zim_version = %s '
        'WHERE b.b_id = %s', (selection_version, builder.b_id))
  wp10db.commit()
  return True


def auto_handle_zim_generation(redis, wp10db, builder_id):
  # First, cancel any pending auto-scheduled tasks.
  for task_id in pending_zim_tasks_for(wp10db, builder_id):
    try:
      zimfarm.cancel_zim_by_task_id(redis, task_id)
      logic_selection.update_zimfarm_task(wp10db, task_id, 'CANCELLED')
    except ZimFarmError:
      logging.exception('Could not cancel task_id=%s', task_id)

  zim_file = latest_zim_file_for(wp10db, builder_id)
  zim_schedule: ZimSchedule = logic_zim_schedules.get_zim_schedule_by_zim_file_id(wp10db, zim_file.z_id)
  title = zim_schedule.s_title.decode(
      'utf-8') if zim_schedule.s_title is not None else None
  description = zim_schedule.s_description.decode(
      'utf-8') if zim_schedule.s_description is not None else None
  long_description = zim_schedule.s_long_description.decode(
      'utf-8') if zim_schedule.s_long_description is not None else None
  handle_zim_generation(redis,
                        wp10db,
                        builder_id,
                        title=title,
                        description=description,
                        long_description=long_description)


def pending_zim_tasks_for(wp10db, builder_id):
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''SELECT z.z_task_id FROM zim_tasks z
           JOIN selections s
             ON s.s_id = z.z_selection_id
           JOIN builders b
             ON b.b_id = s.s_builder_id
           WHERE b.b_id = %s AND z.z_status = "REQUESTED"
    ''', (builder_id,))
    data = cursor.fetchall()
    if data is None:
      return []
    else:
      return [d['z_task_id'].decode('utf-8') for d in data]


def update_version_for_finished_zim(wp10db, task_id):
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''UPDATE builders b
           LEFT JOIN selections s
             ON s.s_builder_id = b.b_id
           LEFT JOIN zim_tasks z
             ON z.z_selection_id = s.s_id
           SET b.b_selection_zim_version = s.s_version
           WHERE z.z_task_id = %s''', (task_id,))
  wp10db.commit()


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


def local_url_for_latest_zim(builder_id):
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


def latest_zim_file_for(wp10db, builder_id) -> ZimTask:
  """Returns the ZIM file that matches the ZIM version of the Builder."""
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''SELECT z.* FROM zim_tasks z
           INNER JOIN selections s
             ON s.s_id = z.z_selection_id
           INNER JOIN builders b
             ON b.b_selection_zim_version = s.s_version
             AND b.b_id = s.s_builder_id
           WHERE b.b_id = %s
        ''', (builder_id,))
    db_zim = cursor.fetchone()
    if db_zim is None:
      return None
    return ZimTask(**db_zim)


def zim_file_for_latest_selection(wp10db, builder_id) -> ZimTask:
  """Returns the ZIM file of the latest Selection for a Builder."""
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''SELECT z.* FROM zim_tasks z
           INNER JOIN selections s
             ON s.s_id = z.z_selection_id
           INNER JOIN builders b
             ON b.b_current_version = s.s_version
             AND b.b_id = s.s_builder_id
           WHERE b.b_id = %s
        ''', (builder_id,))
    db_zim = cursor.fetchone()
    if db_zim is None:
      return None
    return ZimTask(**db_zim)


def latest_zim_file_url_for(wp10db, builder_id):
  zim = latest_zim_file_for(wp10db, builder_id)

  if zim is None or zim.z_status != b'FILE_READY':
    logger.warning('Attempt to get ZIM URL before file ready, builder id=%s',
                   builder_id)
    return None

  return zimfarm.zim_file_url_for_task_id(zim.z_task_id)


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

def request_zim_file_task_for_builder(redis: Redis,
                                      wp10db: Connection,
                                      builder: Builder,
                                      zim_schedule_id: bytes) -> ZimTask:
  """
  Requests a ZIM file from the Zimfarm for the given builder.
  Returns the entire ZimTask object instead of just the z_id.
  """
  task_id = zimfarm.request_zimfarm_task(redis, wp10db, builder, zim_schedule_id)
  selection = latest_selection_for(wp10db, builder.b_id,
           'text/tab-separated-values')

  with wp10db.cursor() as cursor:
    cursor.execute(
      '''UPDATE zim_tasks SET
      z_status = 'REQUESTED', z_task_id = %s, z_zim_schedule_id = %s, z_requested_at = %s
      WHERE z_selection_id = %s
      ''', (task_id, zim_schedule_id, utcnow().strftime(TS_FORMAT_WP10), selection.s_id))
    cursor.execute(
      '''SELECT * FROM zim_tasks WHERE z_selection_id = %s''',
      (selection.s_id,))
    row = cursor.fetchone()
    zim_file = ZimTask(**row) if row else None
  wp10db.commit()
  return zim_file

def request_scheduled_zim_file_for_builder(builder: Builder, zim_schedule_id: bytes):
  """
  Requests a scheduled ZIM file generation from the Zimfarm for the given builder.
  It will reopen connections and rebuild the selection for the builder.
  This is used for scheduled ZIM file generations.
  """

  # Reconnect to the databases and storage (this is needed for scheduled tasks)
  wp10db = wp10_connect()
  redis = redis_connect()
  s3 = connect_storage()

  # Rebuild the selection for the builder
  builder: Builder = get_builder(wp10db, builder.b_id)
  try:
      builder_cls = get_builder_module_class(builder.b_model.decode('utf-8'))
  except ImportError as e:
      logger.error(f"Failed to load builder module class: {e}")
      raise
  materialize_builder(builder_cls, builder, 'text/tab-separated-values', s3, redis, wp10db)

  if zim_schedule_id is None:
    return None 

  task_id = request_zim_file_task_for_builder(redis, wp10db, builder, zim_schedule_id=zim_schedule_id)

  return task_id


def handle_zim_generation(redis,
                          wp10db,
                          builder_id,
                          user_id=None,
                          title='',
                          description='',
                          long_description=None,
                          scheduled_repetitions=None):
  """
  Handles the ZIM file generation and scheduling for a builder.
  """
  
  if isinstance(builder_id, str):
    builder_id = builder_id.encode('utf-8')

  builder = get_builder(wp10db, builder_id)
  if builder is None:
    raise ObjectNotFoundError('Could not find builder with id = %s' %
                              builder_id)

  if user_id is not None:
    user_id = str(user_id)
    builder_user_id = builder.b_user_id.decode('utf-8')
    if user_id != builder_user_id:
      raise UserNotAuthorizedError(
          'Could not use builder id = %s for user id = %s' %
          (builder_id, user_id))

  zim_schedule = zimfarm.create_or_update_zimfarm_schedule(
    redis, wp10db, builder,
    title=title,
    description=description,
    long_description=long_description
  )
  zim_file: ZimTask = request_zim_file_task_for_builder(redis, wp10db, builder, zim_schedule.s_id)

  # If scheduled_repetitions is set, schedule future ZIM file generations
  if scheduled_repetitions is not None:
    logic_zim_schedules.schedule_future_zimfile_generations(
      redis, wp10db, builder, zim_schedule.s_id, scheduled_repetitions
    )

  # In production, there is a web hook from the Zimfarm that notifies us
  # that the task is finished and we can start polling for the ZIM file
  # to be uploaded. The web hook obviously doesn't work in development
  # because the localhost server is not routable. To make ZIM file
  # creation work end to end, start polling immediately in Development.
  if ENV == Environment.DEVELOPMENT:
    logger.info('DEVELOPMENT: Polling for zim file status for task_id=%s',
                zim_file.z_task_id)
    queues.poll_for_zim_file_status(redis, zim_file.z_task_id)

  return zim_file.z_task_id


def zim_file_status_for(wp10db, builder_id):
  data = {
      'status': None,
      'error_url': None,
      'is_deleted': None,
      'description': None,
      'long_description': None,
  }
  zim_file = zim_file_for_latest_selection(wp10db, builder_id)
  if not zim_file:
    return data

  base_url = zimfarm.get_zimfarm_url()
  data['status'] = zim_file.z_status.decode('utf-8')
  if zim_file.z_task_id:
    data['error_url'] = '%s/tasks/%s' % (base_url,
                                         zim_file.z_task_id.decode('utf-8'))
  if zim_file.z_updated_at:
    data['is_deleted'] = logic_selection.is_zim_file_deleted(
        logic_util.wp10_timestamp_to_unix(zim_file.z_updated_at))
  zim_schedule: ZimSchedule = logic_zim_schedules.get_zim_schedule_by_zim_file_id(wp10db, zim_file.z_id)
  data['title'] = zim_schedule.s_title.decode(
      'utf-8') if zim_schedule.s_title else None
  data['description'] = zim_schedule.s_description.decode(
      'utf-8') if zim_schedule.s_description else None
  data['long_description'] = zim_schedule.s_long_description.decode(
      'utf-8') if zim_schedule.s_long_description else None

  return data


def on_zim_file_status_poll(task_id):
  wp10db = wp10_connect()
  redis = redis_connect()
  app_logging.configure_logging()

  result = zimfarm.is_zim_file_ready(task_id)
  logging.info('Polled for ZIM file for task_id=%s, result: %s', task_id,
               result)
  if result == 'FILE_READY':
    logic_selection.update_zimfarm_task(wp10db,
                                        task_id,
                                        'FILE_READY',
                                        set_updated_now=True)
    update_version_for_finished_zim(wp10db, task_id)
  elif result == 'REQUESTED':
    requested = logic_selection.zim_file_requested_at_for(wp10db, task_id)
    if requested is not None:
      now = utcnow().timestamp()
      if now - requested > MAX_ZIM_FILE_POLL_TIME:
        logic_selection.update_zimfarm_task(wp10db, task_id, 'FAILED')
        return

    # There was no requested time, or the time hasn't expired, re-request
    queues.poll_for_zim_file_status(redis, task_id)
  elif result == 'FAILED':
    logic_selection.update_zimfarm_task(wp10db, task_id, 'FAILED')

  wp10db.close()


def _get_builder_data(builder):
  return {
      'id': builder['b_id'].decode('utf-8'),
      'name': builder['b_name'].decode('utf-8'),
      'project': builder['b_project'].decode('utf-8'),
      'model': builder['b_model'].decode('utf-8'),
      'created_at': logic_util.wp10_timestamp_to_unix(builder['b_created_at']),
      'updated_at': logic_util.wp10_timestamp_to_unix(builder['b_updated_at']),
  }


def _get_selection_data(builder):
  data = {
      's_id': None,
      's_updated_at': None,
      's_content_type': None,
      's_extension': None,
      's_url': None,
      's_status': None,
  }

  has_selection = builder['s_id'] is not None
  has_status = builder['s_status'] is not None
  is_ok_status = builder['s_status'] == b'OK'

  if has_selection:
    content_type = builder['s_content_type'].decode('utf-8')
    data['s_id'] = builder['s_id'].decode('utf-8')
    data['s_updated_at'] = logic_util.wp10_timestamp_to_unix(
        builder['s_updated_at'])
    data['s_content_type'] = content_type
    data['s_extension'] = CONTENT_TYPE_TO_EXT.get(content_type, '???')
    if has_status:
      data['s_status'] = builder['s_status'].decode('utf-8')

    if is_ok_status or not has_status:
      data['s_url'] = latest_url_for(builder['b_id'].decode('utf-8'),
                                     content_type)

  return data


def _get_zimfile_data(builder):
  data = {
      'z_status': None,
      'z_updated_at': None,
      'z_url': None,
      'z_is_deleted': None,
  }

  has_selection = builder['s_id'] is not None
  has_zim = builder['z_id'] is not None
  is_zim_ready = builder['z_status'] == b'FILE_READY'

  if has_selection:
    if has_zim:
      content_type = builder['s_content_type'].decode('utf-8')
      data['z_status'] = builder['z_status'].decode('utf-8')
      if builder['z_updated_at'] is not None:
        data['z_updated_at'] = logic_util.wp10_timestamp_to_unix(
            builder['z_updated_at'])
        # Older than 2 weeks are deleted.
        data['z_is_deleted'] = logic_selection.is_zim_file_deleted(
            data['z_updated_at'])
      if content_type == 'text/tab-separated-values' and is_zim_ready:
        data['z_url'] = local_url_for_latest_zim(
            builder['b_id'].decode('utf-8'))
    else:
      data['z_status'] = 'NOT_REQUESTED'

  return data


def get_builders_with_selections(wp10db, user_id):
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''SELECT * FROM builders b
           LEFT JOIN selections s
             ON s.s_builder_id = b.b_id
             AND s.s_version = b.b_current_version
           LEFT JOIN selections s1
             ON s1.s_builder_id = b.b_id
             AND s1.s_version = b.b_selection_zim_version
           LEFT JOIN zim_tasks z
             ON z.z_selection_id = s1.s_id
           WHERE b_user_id = %s
           ORDER BY b.b_updated_at DESC
      ''', (user_id,))
    data = cursor.fetchall()

  result = []
  for db_builder in data:
    builder = {}
    builder.update(_get_builder_data(db_builder))
    builder.update(_get_selection_data(db_builder))
    builder.update(_get_zimfile_data(db_builder))
    result.append(builder)

  return result
