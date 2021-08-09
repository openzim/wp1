import attr
from wp1.models.wp10.builder import Builder
from wp1.wp10_db import connect as wp10_connect


def generate_builder(data, user_id, wp10db):
  params = str({'list': data['articles'].split('\n')})
  builder = Builder(b_name=data['list_name'],
                    b_user_id=user_id,
                    b_model='wp1.selection.models.simple',
                    b_project=data['project'],
                    b_params=params)
  builder.set_created_at_now()
  builder.set_updated_at_now()
  insert_builder(builder, wp10db)


def insert_builder(builder, wp10db):
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''INSERT INTO builders
        (b_name, b_user_id, b_project, b_params, b_model, b_created_at, b_updated_at)
        VALUES (%(b_name)s, %(b_user_id)s, %(b_project)s, %(b_params)s, %(b_model)s, %(b_created_at)s, %(b_updated_at)s)
      ''', attr.asdict(builder))
  wp10db.commit()
