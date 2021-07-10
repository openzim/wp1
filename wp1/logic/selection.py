import io
import urllib.parse

import attr

from wp1.constants import SIMPLE_LIST_MODEL
from wp1.models.wp10.selection import Selection


def validate_list(items):
  item_list = items.split("\n")
  invalid_article_names = []
  valid_article_names = []
  forbiden_chars = []
  for item in item_list:
    is_valid = True
    item = item.strip().replace(" ", "_")
    decoded_item = urllib.parse.unquote(item)
    len_item = len(decoded_item.encode("utf-8"))
    char_set = ["#", "<", ">", "[", "]", "{", "}", "|"]
    if len_item > 256:
      forbiden_chars.append('length greater than 256 bytes')
      invalid_article_names.append(decoded_item)
      is_valid = False
      continue
    for forbiden_character in char_set:
      if forbiden_character in decoded_item:
        forbiden_chars.append(forbiden_character)
        if is_valid:
          invalid_article_names.append(decoded_item)
        is_valid = False
    if is_valid:
      article_name = decoded_item.replace(
          "https://en.wikipedia.org/wiki/",
          "").replace("https://en.wikipedia.org/w/index.php?title=", "")
      valid_article_names.append(article_name)
  return (valid_article_names, invalid_article_names, forbiden_chars)


def _insert_selection(wp10db, selection):
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''INSERT INTO
           selections (s_name, s_user_id, s_project, s_model,
                       s_last_generated, s_created_at)
           VALUES
           (%(s_name)s, %(s_user_id)s, %(s_project)s, %(s_model)s,
            %(s_last_generated)s, %(s_created_at)s)
    ''', attr.asdict(selection))
    return cursor.lastrowid
  wp10db.commit()


def _update_selection(wp10db, selection):
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''UPDATE selections SET
           s_name = %(s_name)s, s_user_id = %(s_user_id)s, s_project = %(s_project)s,
           s_model = %(s_model)s, s_last_generated = %(s_last_generated)s,
           s_bucket = %(s_bucket)s, s_region = %(s_region)s, s_object_key = %(s_object_key)s,
           s_hash = %(s_hash)s, s_created_at = %(s_created_at)s
           WHERE s_id = %(s_id)s
    ''', attr.asdict(selection))
  wp10db.commit()


def _delete_selection(wp10db, id_):
  with wp10db.cursor() as cursor:
    cursor.execute('DELETE FROM selections WHERE s_id = %s', (id_,))
  wp10db.commit()


def _upload_to_storage(s3, selection):
  selection.s_bucket = s3.bucket_name.encode('utf-8')
  selection.s_region = s3.region.encode('utf-8')

  upload_data = io.BytesIO()
  upload_data.write(selection.data)
  upload_data.seek(0)
  s3.upload_fileobj(upload_data, key=selection.s_object_key.decode('utf-8'))


def persist_simple_list(wp10db, s3, name, user_id, project, article_names):
  selection = Selection(name.encode('utf-8'),
                        int(user_id),
                        project.encode('utf-8'),
                        s_model=SIMPLE_LIST_MODEL.encode('utf-8'))
  selection.set_last_generated_now()
  selection.set_created_at_now()
  selection.data = '\n'.join(article_names).encode('utf-8')

  id_ = _insert_selection(wp10db, selection)
  selection.calculate_from_id(id_)

  try:
    _upload_to_storage(s3, selection)
  except:
    _delete_selection(wp10db, selection.s_id)
    raise

  _update_selection(wp10db, selection)
  return True
