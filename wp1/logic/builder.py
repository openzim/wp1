import json
import logging

import attr

from wp1.constants import CONTENT_TYPE_TO_EXT, EXT_TO_CONTENT_TYPE
from wp1.credentials import CREDENTIALS, ENV
import wp1.logic.selection as logic_selection
import wp1.logic.util as logic_util
from wp1.models.wp10.builder import Builder
from wp1.storage import connect_storage
from wp1.wp10_db import connect as wp10_connect

logger = logging.getLogger(__name__)


def create_or_update_builder(wp10db,
                             name,
                             user_id,
                             project,
                             articles,
                             builder_id=None):
  params = json.dumps({'list': articles.split('\n')}).encode('utf-8')
  builder = Builder(b_name=name,
                    b_user_id=user_id,
                    b_model='wp1.selection.models.simple',
                    b_project=project,
                    b_params=params)
  builder.set_updated_at_now()
  if builder_id is None:
    builder.set_created_at_now()
    return insert_builder(wp10db, builder)

  builder.b_id = int(builder_id)
  if update_builder(wp10db, builder):
    return builder_id

  return None


def insert_builder(wp10db, builder):
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''INSERT INTO builders
        (b_name, b_user_id, b_project, b_params, b_model, b_created_at, b_updated_at)
        VALUES (%(b_name)s, %(b_user_id)s, %(b_project)s, %(b_params)s, %(b_model)s, %(b_created_at)s, %(b_updated_at)s)
      ''', attr.asdict(builder))
    id_ = cursor.lastrowid
  wp10db.commit()
  return id_


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
      SET b_name = %(b_name)s, b_project = %(b_project)s, b_params = %(b_params)s, b_model = %(b_model)s,
          b_updated_at = %(b_updated_at)s
      WHERE b_id = %(b_id)s AND b_user_id = %(b_user_id)s
      ''', attr.asdict(builder))
    rowcount = cursor.rowcount
  wp10db.commit()
  return rowcount > 0


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


def latest_selection_url(wp10db, builder_id, ext):
  content_type = EXT_TO_CONTENT_TYPE.get(ext)
  if content_type is None:
    logger.warning(
        'Attempt to get latest selection with unrecognized extension: %r', ext)
    return None

  with wp10db.cursor() as cursor:
    cursor.execute(
        '''SELECT s.s_object_key AS object_key
           FROM selections AS s JOIN builders as b
             ON s.s_builder_id = b.b_id
             AND s.s_version = b.b_current_version
             AND s.s_content_type = %s
           WHERE b.b_id = %s''', (content_type, builder_id))
    data = cursor.fetchone()
  if data is None:
    logger.warning('Could not find latest selection for builder id=%s',
                   builder_id)
    return None

  return logic_selection.url_for(data['object_key'].decode('utf-8'))


def get_builders_with_selections(wp10db, user_id):
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''SELECT * FROM selections
           RIGHT JOIN builders
             ON selections.s_builder_id=builders.b_id
             AND selections.s_version=builders.b_current_version
           WHERE b_user_id=%(b_user_id)s
           ORDER BY selections.s_id ASC''', {'b_user_id': user_id})
    data = cursor.fetchall()

    builders = {}
    result = []
    for b in data:
      has_selection = b['s_id'] is not None
      content_type = b['s_content_type'].decode(
          'utf-8') if has_selection else None
      selection_id = b['s_id'].decode('utf-8') if has_selection else None
      result.append({
          'id':
              b['b_id'],
          'name':
              b['b_name'].decode('utf-8'),
          'project':
              b['b_project'].decode('utf-8'),
          'created_at':
              logic_util.wp10_timestamp_to_unix(b['b_created_at']),
          'updated_at':
              logic_util.wp10_timestamp_to_unix(b['b_updated_at']),
          's_id':
              selection_id,
          's_updated_at':
              logic_util.wp10_timestamp_to_unix(b['s_updated_at'])
              if has_selection else None,
          's_content_type':
              content_type,
          's_extension':
              CONTENT_TYPE_TO_EXT.get(content_type, '???')
              if has_selection else None,
          's_url':
              latest_url_for(b['b_id'], content_type)
              if has_selection else None,
      })
    return result
