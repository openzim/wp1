import urllib.parse
from wp1.selection.abstract_builder import AbstractBuilder


class SimpleBuilder(AbstractBuilder):

  def _validate_list(self, **params):
    if not params['list']:
      return ([], [], ['Empty List'])
    invalid_article_names = []
    valid_article_names = []
    forbiden_chars = []
    for item in params['list']:
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

  def build(self, content_type, **params):
    if len(params) == 1:
      if 'list' in params.keys():
        return '\n'.join(params['list']).encode('utf-8')
      KeyError('Incorrect params present')
    ValueError('Unwanted params present')

  def validate(self, **params):
    valid_names, invalid_names, forbiden_chars = self._validate_list(**params)
    if forbiden_chars[0] != 'Empty List':
      forbiden_chars.insert(
          0, 'The list contained the following invalid characters: ')
    return (valid_names, invalid_names, forbiden_chars)
