import attr


def insert_(wp10db, builder):
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''INSERT INTO builders
      (b_name, b_user_id, b_project, b_params)
      VALUES (%(b_name)s, %(b_user_id)s, %(b_project)s, %(b_params)s)
    ''', attr.asdict(builder))
  wp10db.commit()
