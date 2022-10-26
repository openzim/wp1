import logging

from wp1.custom_tables.base_custom_table import BaseCustomTable
from wp1.templates import env as jinja_env

logger = logging.getLogger(__name__)


class CustomTable(BaseCustomTable):

  def __init__(self, **kwargs):
    self.params = kwargs

  def generate(self, wp10db):
    projects = []
    for project in self.params["projects"]:
      out = {}
      for key in ('bgcolor', 'name', 'alias'):
        if key in project:
          out[key] = project[key]
      out['data'] = [1, 2, 3, 4, 5, 6, 7]
      projects.append(out)

    # print(repr(projects))
    return {'projects': projects}

  def create_wikicode(self, table_data):
    template_path = self.params.get('template')
    if template_path is None:
      logger.error(
          'Params for custom table %s missing template path.'
          ' Upload cannot continue.', self.params.get('name', 'unknown-table'))
      return

    template = jinja_env.get_template(template_path)
    wikicode = template.render(table_data)
    # print(wikicode)
    return wikicode
