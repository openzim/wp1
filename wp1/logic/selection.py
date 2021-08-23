import attr

from wp1.constants import CONTENT_TYPE_TO_EXT


def insert_selection(wp10db, selection):
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''INSERT INTO selections
      (s_id, s_builder_id, s_content_type, s_updated_at)
      VALUES (%(s_id)s, %(s_builder_id)s, %(s_content_type)s, %(s_updated_at)s)
    ''', attr.asdict(selection))
  wp10db.commit()


def object_key_for_selection(selection, model):
  if not selection:
    raise ValueError('Cannot get object key for None selection')
  if not model:
    raise ValueError('Expected WP1 model name, got: %r' % model)
  ext = CONTENT_TYPE_TO_EXT.get(selection.s_content_type, '???')
  return 'selections/%(model)s/%(id)s.%(ext)s' % {
      'model': model,
      'id': selection.s_id.decode('utf-8'),
      'ext': ext,
  }
