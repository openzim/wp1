import logging
import time

from conf import get_conf
import constants
from logic import page as logic_page, release as logic_release
from models.wiki.page import Page
from models.wp10.release import Release
from wp10_db import Session as SessionWP10
from wiki_db import Session as SessionWiki

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

wp10_session = SessionWP10()
wiki_session = SessionWiki()

category_name = b'Version_1.0_articles_by_category';
suffix = b'_Version_1.0_articles';

config = get_conf()
category_ns = config['CATEGORY_NS'].encode('utf-8')

def get_title_to_release():
  q = wp10_session.query(Release)
  logger.info('Querying release data')
  return dict((release.article, release) for release in q)

def extract_release_category(title):
  return title.replace(suffix, b'').replace(category_ns, b'')

title_to_release = get_title_to_release()

seen = set()
for category_page in logic_page.get_pages_by_category(
    wiki_session, category_name):
  logging.info('Processing category: %r', category_page.title)
  release_category = extract_release_category(category_page.title)

  for page in logic_page.get_pages_by_category(
      wiki_session, category_page.title, ns=constants.CATEGORY_NS_INT):
    seen.add(page.title)
    release = title_to_release.get(page.title)
    if release is None or release.category != release_category:
      logic_release.insert_or_update_release_data(
        wp10_session, page.title, release_category, page.timestamp)
  wp10_session.commit()

for title in title_to_release.keys():
  if title not in seen:
    logger.info('Page not seen, setting release data to "None": %s', title)
    logic_release.insert_or_update_release_data(
      wp10_session, title, 'None', time.time())
wp10_session.commit()
