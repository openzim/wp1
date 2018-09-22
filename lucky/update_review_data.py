import time

from conf import get_conf
from logic import review
from models.wiki.page import Page
from models.wp10.review import Review
from wp10_db import Session as SessionWP10
from wiki_db import Session as SessionWiki

wp10_session = SessionWP10()
wiki_session = SessionWiki()

def get_pages_by_category(category):
    yield from wiki_session.query(Page).filter(Page.category == category)

def get_title_to_value():
    q = wp10_session.query(Review)
    return dict((review.article, review.value) for review in q)

review_value_to_category = get_conf()['REVIEW']

title_to_value = get_title_to_value()

for value, category in review_value_to_category.items():
    value = value.encode('utf-8')
    category = category.encode('utf-8')
    for page in get_pages_by_category(category):
        old_value = title_to_value.get(page.title)
        if old_value is None or old_value != value:
            review.update_review_data(
                wp10_session, page.title, value, page.timestamp)
    wp10_session.commit()
