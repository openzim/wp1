from wp1.logic.selection import validate_list
from wp1.selection.abstract_builder import AbstractBuilder


class SimpleBuilder(AbstractBuilder):

  def build(self, content_type, **params):
    return '\n'.join(params['list']).encode('utf-8')

  def validate(self, **params):
    valid_names, invalid_names, forbiden_chars = validate_list(params['list'])
    return (valid_names, invalid_names, [
        'The list contained the following invalid characters: ', forbiden_chars
    ])
