import attr
import json
from wp1.models.wp10.builder import Builder
from wp1.wp10_db import connect as wp10_connect


def save_builder(wp10db, name, user_id, project, articles):
  params = json.dumps({'list': articles.split('\n')}).encode('utf-8')
  builder = Builder(b_name=name,
                    b_user_id=user_id,
                    b_model='wp1.selection.models.simple',
                    b_project=project,
                    b_params=params)
  builder.set_created_at_now()
  builder.set_updated_at_now()
  insert_builder(wp10db, builder)


def insert_builder(wp10db, builder):
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''INSERT INTO builders
        (b_name, b_user_id, b_project, b_params, b_model, b_created_at, b_updated_at)
        VALUES (%(b_name)s, %(b_user_id)s, %(b_project)s, %(b_params)s, %(b_model)s, %(b_created_at)s, %(b_updated_at)s)
      ''', attr.asdict(builder))
  wp10db.commit()
