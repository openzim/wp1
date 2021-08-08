import attr
import urllib.parse
from wp1.models.wp10.builder import Builder
from flask import session
from wp1.selection.abstract_builder import AbstractBuilder


class SimpleBuilder(AbstractBuilder):

  def build(self, content_type, **params):
    if content_type != 'text/tab-separated-values':
      raise ValueError('Unrecognized content type')
    if len(params) == 1:
      if 'list' in params:
        return '\n'.join(params['list']).encode('utf-8')
      raise ValueError(
          f'Missing required param: list, unnecessary argument given: {list(params.keys())[0]}'
      )
    raise ValueError('Additional unnecessary params present')

  def validate(self, **params):
    if not params['list']:
      return ([], [], ['Empty List'])
    invalid_article_names = []
    valid_article_names = []
    forbidden_chars = []
    errors = []
    for item in params['list']:
      is_valid = True
      item = item.strip().replace(" ", "_")
      decoded_item = urllib.parse.unquote(item)
      len_item = len(decoded_item.encode("utf-8"))
      char_set = ["#", "<", ">", "[", "]", "{", "}", "|"]
      for forbidden_character in char_set:
        if forbidden_character in decoded_item:
          forbidden_chars.append(forbidden_character)
          if is_valid:
            invalid_article_names.append(decoded_item)
            is_valid = False
      if len_item > 256:
        errors.append('The list contained an item longer than 256 bytes')
        invalid_article_names.append(decoded_item)
        is_valid = False
      if is_valid:
        article_name = decoded_item.replace(
            "https://en.wikipedia.org/wiki/",
            "").replace("https://en.wikipedia.org/w/index.php?title=", "")
        valid_article_names.append(article_name)
    if forbidden_chars:
      errors.append('The list contained the following invalid characters: ' +
                    ', '.join(forbidden_chars))
    return (valid_article_names, invalid_article_names, errors)

  def insert_builder(self, data, wp10db):
    params = str({'list': data['articles'].split('\n')})
    builder = Builder(b_name=data['list_name'],
                      b_user_id=session['user']['identity']['sub'],
                      b_model='wp1.selection.models.simple',
                      b_project=data['project'],
                      b_params=params)
    builder.set_created_at_now()
    builder.set_updated_at_now()
    with wp10db.cursor() as cursor:
      cursor.execute(
          '''INSERT INTO builders
        (b_name, b_user_id, b_project, b_params, b_model, b_created_at, b_updated_at)
        VALUES (%(b_name)s, %(b_user_id)s, %(b_project)s, %(b_params)s, %(b_model)s, %(b_created_at)s, %(b_updated_at)s)
      ''', attr.asdict(builder))
    wp10db.commit()

  def get_lists(self, wp10db):
    with wp10db.cursor() as cursor:
      cursor.execute('SELECT * FROM builders WHERE b_user_id=%(b_user_id)s',
                     {'b_user_id': session['user']['identity']['sub']})
      db_lists = cursor.fetchall()
      if db_lists is None:
        return None

      return {'article_lists': db_lists}
