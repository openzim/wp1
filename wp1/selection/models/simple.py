import urllib.parse

from wp1.exceptions import Wp1FatalSelectionError
from wp1.selection.abstract_builder import AbstractBuilder


class Builder(AbstractBuilder):
  '''
  Model for validating and building (materializing) Simple builders.

  The 'validate' method takes in the parameters to the model in kwargs format
  and returns a tuple of three items: A list with the valid values, a list with
  the invalid values, and a list of error messages. So ([], [], []). If the
  second or third items are truthy, it is considered an error.

  The 'build' method takes in the same parameters and materializes the builder
  into a selection. This means taking those parameters and producing a newline
  separated string which represents an article list, that will be uploaded
  directly to S3-like storage as the selection contents.

  Both of these methods are called by the backend API and the AbstractBuilder
  abstract class.
  '''

  MAX_LIST_SIZE = 1024 * 1024 * 10  # 10 MB
  MAX_LIST_DESC = '10 MB'

  def build(self, content_type, **params):
    if content_type != 'text/tab-separated-values':
      raise Wp1FatalSelectionError('Unrecognized content type')
    if 'list' not in params:
      raise Wp1FatalSelectionError('Missing required param: list')

    list_minus_comments = [
        line.strip()
        for line in params['list']
        if line.strip() != '' and not line.startswith('#')
    ]
    return '\n'.join(list_minus_comments).encode('utf-8')

  def validate(self, **params):
    if not params['list']:
      return ([], [], ['Empty List'])
    if len(('').join(params['list'])) > self.MAX_LIST_SIZE:
      return ([], [], ['The list was longer than %s' % self.MAX_LIST_DESC])

    invalid_article_names = []
    valid_article_names = []
    forbidden_chars = []
    errors = []
    for item in params['list']:
      is_valid = True
      item = item.strip().replace(" ", "_")
      # Ignore lines that are only whitespace or that start with a comment
      if item == '' or item.startswith('#'):
        continue
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
