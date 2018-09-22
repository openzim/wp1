import logging

from conf import get_conf
from logic import page as logic_page, review as logic_review
from models.wiki.page import Page
from models.wp10.review import Review
from wp10_db import Session as SessionWP10
from wiki_db import Session as SessionWiki

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

wp10_session = SessionWP10()
wiki_session = SessionWiki()

def get_title_to_value():
  q = wp10_session.query(Review)
  logger.info('Querying review data')
  return dict((review.article, review.value) for review in q)

review_value_to_category = get_conf()['REVIEW']

title_to_value = get_title_to_value()

seen = set()
for value, category in review_value_to_category.items():
  value = value.encode('utf-8')
  category = category.encode('utf-8')
  for page in logic_page.get_pages_by_category(wiki_session, category):
    seen.add(page.title)
    old_value = title_to_value.get(page.title)
    if old_value is None or old_value != value:
      logic_review.insert_or_update_review_data(
        wp10_session, page.title, value, page.timestamp)
  wp10_session.commit()

for title, old_value in title_to_value.items():
  if title not in seen:
    logger.info('Page not seen, removing review data: %s', title)
    logic_review.delete_review_data(wp10_session, title, old_value)
wp10_session.commit()
