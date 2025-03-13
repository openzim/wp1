import logging

from wp1.custom_tables.base_custom_table import BaseCustomTable
from wp1.templates import env as jinja_env

logger = logging.getLogger(__name__)


class CustomTable(BaseCustomTable):

  def __init__(self, **kwargs):
    self.params = kwargs

  def _query_project_article_count(self, wp10db, project_name):
    with wp10db.cursor() as cursor:
      cursor.execute(
          'SELECT count(r_article) AS n, r_quality as quality FROM ratings WHERE r_project = %s '
          'GROUP BY r_project, r_quality', (project_name,))
      return cursor.fetchall()

  def generate(self, wp10db):
    projects = []
    for project in self.params['projects']:
      out = {}
      for key in ('bgcolor', 'name', 'alias'):
        if key in project:
          out[key] = project[key]

      counts = self._query_project_article_count(
          wp10db, project['name'].encode('utf-8'))

      # Map the categories to their counts, filtering out any categories/qualities that
      # aren't going to be used in the final output. Add an entry with value '0' for any
      # categories that failed to appear.
      counts_by_cat = dict(
          (c['quality'], c['n'])
          for c in counts
          if c['quality'].decode('utf-8') in self.params['categories'])
      for cat in self.params['categories']:
        encoded = cat.encode('utf-8')
        if encoded not in counts_by_cat:
          counts_by_cat[encoded] = 0

      # Sort by the original ordering in the categories param
      data = sorted(
          counts_by_cat.items(),
          key=lambda d: self.params['categories'].index(d[0].decode('utf-8')))
      # Keep only the counts
      out['data'] = [d[1] for d in data]

      total = 0
      wikiwork = 0
      for i, d in enumerate(out['data']):
        total += d
        wikiwork += d * i
      out['data'] += [
          total, wikiwork, f'{wikiwork / total:.3f}' if total > 0 else '-'
      ]

      projects.append(out)

    data = {}
    for key in ('parent_project', 'categories', 'aggregate_name'):
      if key in self.params:
        data[key] = self.params[key]
    data['projects'] = projects
    return data

  def create_wikicode(self, table_data):
    template_path = self.params.get('template')
    if template_path is None:
      logger.error(
          'Params for custom table %s missing template path.'
          ' Upload cannot continue.', self.params.get('name', 'unknown-table'))
      return

    template = jinja_env.get_template(template_path)
    wikicode = template.render(table_data)
    return wikicode
