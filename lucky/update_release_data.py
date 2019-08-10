from datetime import datetime
import logging

from lucky.conf import get_conf
from lucky import constants
from lucky.logic import page as logic_page, release as logic_release
from lucky.models.wiki.page import Page
from lucky.models.wp10.release import Release
from lucky.wp10_db import conn as wp10db
from lucky.wiki_db import conn as wikidb

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

category_name = b'Version_1.0_articles_by_category';
suffix = b'_Version_1.0_articles';

config = get_conf()
category_ns = config['CATEGORY_NS'].encode('utf-8')


def extract_release_category(title):
  return title.replace(suffix, b'').replace(category_ns, b'')


def main():
  title_to_release = logic_release.get_title_to_release()

  seen = set()
  for category_page in logic_page.get_pages_by_category(
      wiki_db, category_name):
    logging.info(
      'Processing category: %r', category_page.page_title.encode('utf-8'))
    release_category = extract_release_category(category_page.page_title)

    for page in logic_page.get_pages_by_category(
        wiki_db, category_page.page_title, ns=constants.CATEGORY_NS_INT):
      seen.add(page.page_title)
      release = title_to_release.get(page.page_title)
      if release is None or release.category != release_category:
        logic_release.insert_or_update_release_data(
          wp10_session, page.page_title, release_category, page.cl_timestamp)
    wp10db.commit()

  for title in title_to_release.keys():
    if title not in seen:
      logger.info('Page not seen, setting release data to "None": %s', title)
      logic_release.insert_or_update_release_data(
        wp10db, title, b'None', datetime.now())
  wp10db.commit()

if __name__ == '__main__':
  main()
