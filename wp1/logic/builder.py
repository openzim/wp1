import json
import logging

import attr

from wp1.constants import CONTENT_TYPE_TO_EXT
import wp1.logic.selection as logic_selection
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


def get_builders_with_selections(wp10db, user_id):
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''SELECT * FROM selections
                      RIGHT JOIN builders ON selections.s_builder_id=builders.b_id
                      WHERE b_user_id=%(b_user_id)s
                      ORDER BY selections.s_id ASC''', {'b_user_id': user_id})
    data = cursor.fetchall()

    builders = {}
    result = []
    for b in data:
      if not b['b_id'] in builders:
        builders[b['b_id']] = {
            'name': b['b_name'].decode('utf-8'),
            'project': b['b_project'].decode('utf-8'),
            'selections': [],
        }
      if b['s_id']:
        content_type = b['s_content_type'].decode('utf-8')
        selection_id = b['s_id'].decode('utf-8')
        builders[b['b_id']]['selections'].append({
            'id':
                selection_id,
            'content_type':
                content_type,
            'extension':
                CONTENT_TYPE_TO_EXT.get(content_type, '???'),
            'url':
                logic_selection.url_for(selection_id, content_type,
                                        b['b_model'].decode('utf-8')),
        })
    for id_, value in builders.items():
      result.append({
          'id': id_,
          'name': value['name'],
          'project': value['project'],
          'selections': value['selections'],
      })
    return result
