from wp1.exceptions import Wp1FatalSelectionError
from wp1.selection.abstract_builder import AbstractBuilder


def _get_articles_for_project(wp10db, project):
  with wp10db.cursor() as cursor:
    cursor.execute(
        'SELECT r_article FROM ratings WHERE r_namespace = 0 AND r_project = %s',
        (project.strip().replace(' ', '_'),))
    return [row['r_article'].decode('utf-8') for row in cursor.fetchall()]


def _project_exists(wp10db, project):
  with wp10db.cursor() as cursor:
    cursor.execute('SELECT 1 FROM projects WHERE p_project = %s',
                   (project.replace(' ', '_').encode('utf-8'),))
    return cursor.fetchone() is not None


class Builder(AbstractBuilder):

  def build(self, content_type, **params):
    if content_type != 'text/tab-separated-values':
      raise Wp1FatalSelectionError('Unrecognized content type')
    if 'wp10db' not in params:
      raise Wp1FatalSelectionError('Missing param `wp10db`')
    if 'include' not in params:
      raise Wp1FatalSelectionError('Missing param `include`')
    if not params['include']:
      raise Wp1FatalSelectionError(
          'Cannot create selection with empty `include` list')

    included_articles = set()
    for project in params['include']:
      included_articles.update(
          _get_articles_for_project(params['wp10db'], project))

    excluded_articles = set()
    for project in params.get('exclude', []):
      excluded_articles.update(
          _get_articles_for_project(params['wp10db'], project))

    return '\n'.join(
        included_articles.difference(excluded_articles)).encode('utf-8')

  def validate(self, **params):
    if 'wp10db' not in params:
      raise Wp1FatalSelectionError('Cannot validate without param `wp10db`')
    if 'include' not in params or not params['include']:
      return ([], [], ['Missing articles to include'])

    valid = []
    invalid = []
    for project in params['include'] + params.get('exclude', []):
      if _project_exists(params['wp10db'], project):
        valid.append(project)
      else:
        invalid.append(project)

    errors = []
    if invalid:
      errors = ['Not all given projects exist']

    return (valid, invalid, errors)
