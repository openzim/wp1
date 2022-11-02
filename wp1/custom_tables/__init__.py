import importlib
import json
import logging

from wp1.wp10_db import connect as wp10_connect

logger = logging.getLogger(__name__)


def all_custom_table_names(wp10db):
  with wp10db.cursor() as cursor:
    cursor.execute('SELECT c_name FROM custom WHERE c_is_active = 1')
    return [data['c_name'] for data in cursor.fetchall()]


def upload_custom_table_by_name(custom_name):
  logging.basicConfig(level=logging.INFO)
  wp10db = None

  try:
    wp10db = wp10_connect()
    with wp10db.cursor() as cursor:
      cursor.execute('SELECT c_module, c_params FROM custom WHERE c_name = %s',
                     (custom_name.decode('utf-8'),))
      data = cursor.fetchone()
      if data is None:
        raise ValueError('Could not find custom table with name: %r' %
                         custom_name.decode('utf-8'))

      module = data['c_module'].decode('utf-8')
      try:
        params = json.loads(data['c_params'].decode('utf-8'))
      except json.decoder.JSONDecodeError:
        logger.exception('Could not parse custom table JSON params')
        raise

    wiki_path = params.get('wiki_path')
    if wiki_path is None:
      raise ValueError(
          'Missing "wiki_path" param in table %s params. Upload cannot continue.'
          % custom_name)

    if not module.startswith('wp1.custom_tables'):
      raise ValueError(
          'Expected module path to start with "wp1.custom_tables" but it did not'
      )

    table_module = importlib.import_module(module)
    CustomTable = getattr(table_module, 'CustomTable')

    table = CustomTable(name=custom_name.decode('utf-8'), **params)
    table.upload(wp10db, custom_name, wiki_path)
  finally:
    if wp10db is not None:
      wp10db.close()
