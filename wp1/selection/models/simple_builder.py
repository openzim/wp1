import urllib.parse
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
    error_msg = []
    for item in params['list']:
      is_valid = True
      item = item.strip().replace(" ", "_")
      decoded_item = urllib.parse.unquote(item)
      len_item = len(decoded_item.encode("utf-8"))
      char_set = ["#", "<", ">", "[", "]", "{", "}", "|"]
      for forbiden_character in char_set:
        if forbiden_character in decoded_item:
          forbidden_chars.append(forbiden_character)
          if is_valid:
            invalid_article_names.append(decoded_item)
            is_valid = False
      if len_item > 256:
        error_msg.append('The list contained an item longer than 256 bytes')
        invalid_article_names.append(decoded_item)
        is_valid = False
      if is_valid:
        article_name = decoded_item.replace(
            "https://en.wikipedia.org/wiki/",
            "").replace("https://en.wikipedia.org/w/index.php?title=", "")
        valid_article_names.append(article_name)
    if forbidden_chars:
      error_msg.append('The list contained the following invalid characters: ' +
                       ', '.join(forbidden_chars))
    return (valid_article_names, invalid_article_names, error_msg)
