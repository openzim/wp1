import attr


def insert_selection(wp10db, selection):
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''INSERT INTO selections
      (s_id, s_builder_id, s_content_type, s_updated_at)
      VALUES (%(s_id)s, %(s_builder_id)s, %(s_content_type)s, %(s_updated_at)s)
    ''', attr.asdict(selection))
  wp10db.commit()
