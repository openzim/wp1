import logging

from wp1.custom_tables.base_custom_table import BaseCustomTable
from wp1.templates import env as jinja_env

logger = logging.getLogger(__name__)


class CustomTable(BaseCustomTable):

  def __init__(self, **kwargs):
    self.params = kwargs

  def generate(self, wp10db):
    pass

  def create_wikicode(self, table_data):
    template_path = self.params.get('template')
    if template_path is None:
      logger.error(
          'Params for custom table %s missing template path.'
          ' Upload cannot continue.', self.params.get('name', 'unknown-table'))
      return

    template = jinja_env.get_template(template_path)
