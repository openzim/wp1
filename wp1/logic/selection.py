import attr

from wp1.constants import CONTENT_TYPE_TO_EXT

try:
  from wp1.credentials import ENV, CREDENTIALS
  S3_PUBLIC_URL = CREDENTIALS.get(ENV, {}).get('CLIENT_URL', {}).get(
      's3', 'http://credentials.not.found.fake')
except ImportError:
  S3_PUBLIC_URL = 'http://credentials.not.found.fake'


def insert_selection(wp10db, selection):
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''INSERT INTO selections
      (s_id, s_builder_id, s_content_type, s_updated_at)
      VALUES (%(s_id)s, %(s_builder_id)s, %(s_content_type)s, %(s_updated_at)s)
    ''', attr.asdict(selection))
  wp10db.commit()


def url_for_selection(selection, model):
  if not selection:
    raise ValueError('Cannot get url for None selection')
  return '%s/%s' % (S3_PUBLIC_URL, object_key_for_selection(selection, model))


def url_for(selection_id, content_type, model):
  if not selection_id:
    raise ValueError('Cannot get url for None selection_id')
  if not model:
    raise ValueError('Expected WP1 model name, got: %r' % model)
  return '%s/%s' % (S3_PUBLIC_URL,
                    object_key_for(selection_id, content_type, model))


def object_key_for(selection_id, content_type, model):
  if not selection_id:
    raise ValueError('Cannot get object key for None selection_id')
  if not model:
    raise ValueError('Expected WP1 model name, got: %r' % model)
  ext = CONTENT_TYPE_TO_EXT.get(content_type, '???')
  return 'selections/%(model)s/%(id)s.%(ext)s' % {
      'model': model,
      'id': selection_id,
      'ext': ext,
  }


def object_key_for_selection(selection, model):
  if not selection:
    raise ValueError('Cannot get object key for None selection')
  return object_key_for(selection.s_id.decode('utf-8'),
                        selection.s_content_type.decode('utf-8'), model)
