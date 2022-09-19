from wp1.selection.abstract_builder import AbstractBuilder


class Builder(AbstractBuilder):
  '''
  Model for validating and building (materializing) SPARQL builders.

  A SPARQL list is a SPARQL query that represents a list of articles.

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

  def build(self, content_type, **params):
    return str(params).encode('utf-8')

  def validate(self, **params):
    return ('', '', [])
