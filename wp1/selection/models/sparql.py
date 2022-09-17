from wp1.selection.abstract_builder import AbstractBuilder


class Builder(AbstractBuilder):

  def build(self, content_type, **params):
    return str(params).encode('utf-8')

  def validate(self, **params):
    return ('', '', [])
