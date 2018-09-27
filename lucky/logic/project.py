import logging
import re

from conf import get_conf
from constants import AssessmentKind, CATEGORY_NS_INT
from logic import page as logic_page, util as logic_util
from logic.api import project as api_project
from models.wp10.category import Category
from models.wp10.project import Project
from models.wp10.rating import Rating

logger = logging.getLogger(__name__)

config = get_conf()
CLASS = config['CLASS']
QUALITY = config['QUALITY']
IMPORTANCE = config['IMPORTANCE']

RE_INDICATOR = re.compile(b'([A-Za-z]+)[ _-]')

def update_category(
    wp10_session, project, page, extra, kind, rating_to_page_title):
  extra_category = extra.get(page.title)
  if extra_category is not None:
    rating = extra_category['title']
    ranking = extra_category['ranking']
  else:
    md = RE_INDICATOR.search(page.title)
    if not md:
      logger.debug('Skipping page with no class match: %s', page.title)
      return

    rating = ('%s-%s' % (md.group(1).decode('utf-8'), CLASS))
    if kind == AssessmentKind.QUALITY:
      rating_map = QUALITY
    else:
      rating_map = IMPORTANCE

    if rating not in rating_map:
      logger.debug('Skipping page with unrecognized indicator: %s - %s',
                   page.title, rating)
      return
    ranking = rating_map[rating]

  rating_to_page_title[rating] = page.title

  category = Category(
    project=project.project, type=kind.value.encode('utf-8'),
    rating=rating.encode('utf-8'), category=page.title, ranking=ranking,
    replacement=rating.encode('utf-8'))
  # If there is an existing category, merge in our changes
  category = wp10_session.merge(category)
  wp10_session.add(category)


def update_project_categories_by_kind(
    wiki_session, wp10_session, project, extra, kind):

  rating_to_page_title = {}
  category_name_main = logic_util.category_for_project_by_kind(
    project.project, kind, category_prefix=False)
  category_name_alt = logic_util.category_for_project_by_kind(
    project.project, kind, category_prefix=False, use_alt=True)

  found_page = False
  for category_name in (category_name_main, category_name_alt):
    for page in logic_page.get_pages_by_category(
        wiki_session, category_name, ns=CATEGORY_NS_INT):
      found_page = True
      update_category(
        wp10_session, project, page, extra, kind, rating_to_page_title)

    # There might not be any pages listed "by importance" so we have to check
    # the alternate name ("by priority"), unless we already found pages.
    if found_page:
      break

  return rating_to_page_title

def update_project_assessments(
    wiki_session, wp10_session, project, extra_assessments, kind):
  if kind not in (AssessmentKind.QUALITY, AssessmentKind.IMPORTANCE):
    raise ValueError('Parameter "kind" was not one of QUALITY or IMPORTANCE')

  old_ratings = list(
    wp10_session.query(Rating).filter(Rating.project == project.project))
  new_ratings = []

  seen = set()
  moved = set()

  rating_to_page_title = update_project_categories_by_kind(
    wiki_session, wp10_session, project, extra_assessments, kind)

  for rating, page_title in rating_to_page_title.items():
    logging.info('Fetching article list for %s' % page_title)

def update_project(wiki_session, wp10_session, project):
  extra_assessments = api_project.get_extra_assessments(project.project)
  timestamp = project.timestamp

  for kind in (AssessmentKind.QUALITY, AssessmentKind.IMPORTANCE):
    logger.debug('Updating %s assessments by %s',
                 project.project.decode('utf-8'), kind)
    update_project_assessments(
      wiki_session, wp10_session, project, extra_assessments['extra'], kind)
    wp10_session.commit()
