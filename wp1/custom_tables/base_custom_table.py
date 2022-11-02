import json
import logging

from wp1 import api

logger = logging.getLogger(__name__)


class BaseCustomTable:

  def generate(self):
    raise NotImplementedError(
        'Should be implemented by subclasses to provide data '
        'for custom tables')

  def create_wikicode(self):
    raise NotImplementedError(
        'Should be implemented by subclasses to provide wikicode formatting'
        ' for custom tables')

  def upload(self, wp10db, name, wiki_path):
    """
    Superclass method for CustomTable implementations to handle upload.

    This handles callign subclass methods that query the database for data,
    format it into wikitext, and upload it to English Wikipedia.
    """
    logger.info('Generating custom table in subclass: %s', name.decode('utf-8'))
    table_data = self.generate(wp10db)

    logger.info('Generating custom table wikicode: %s', name.decode('utf-8'))
    wikicode = self.create_wikicode(table_data)

    page_name = ('User:WP 1.0 bot/Tables/Custom/%s' % wiki_path)
    page = api.get_page(page_name)
    logger.info('Uploading wikicode to Wikipedia: %s', name.decode('utf-8'))
    api.save_page(page, wikicode, 'Copying assessment table to wiki.')
