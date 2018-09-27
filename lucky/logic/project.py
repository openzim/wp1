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

def update_project_categories_by_kind(
    wiki_session, wp10_session, project, extra, kind):

  rating_to_page_title = {}
  category_name = logic_util.category_for_project_by_kind(
    project.project, kind, category_prefix=False)

  for page in logic_page.get_pages_by_category(
      wiki_session, category_name, ns=CATEGORY_NS_INT):
    extra_category = extra.get(page.title)
    if extra_category is not None:
      rating = extra_category['title']
      ranking = extra_category['ranking']
    else:
      md = RE_INDICATOR.search(page.title)
      if not md:
        logger.debug('Skipping page with no class match: %s', page.title)
        continue

      rating = ('%s-%s' % (md.group(1).decode('utf-8'), CLASS))
      if kind == AssessmentKind.QUALITY:
        rating_map = QUALITY
      else:
        rating_map = IMPORTANCE

      if rating not in rating_map:
        logger.debug('Skipping page with unrecognized indicator: %s - %s',
                     page.title, rating)
        continue
      ranking = rating_map[rating]

    rating_to_page_title[rating] = page.title

    category = Category(
      project=project.project, type=kind.value.encode('utf-8'),
      rating=rating.encode('utf-8'), category=page.title, ranking=ranking,
      replacement=rating.encode('utf-8'))
    # If there is an existing category, merge in our changes
    category = wp10_session.merge(category)
    wp10_session.add(category)

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

  update_project_categories_by_kind(
    wiki_session, wp10_session, project, extra_assessments, kind)

def update_project(wiki_session, wp10_session, project):
  extra_assessments = api_project.get_extra_assessments(project.project)
  timestamp = project.timestamp

  for kind in (AssessmentKind.QUALITY, AssessmentKind.IMPORTANCE):
    logger.debug('Updating %s assessments by %s',
                 project.project.decode('utf-8'), kind)
    update_project_assessments(
      wiki_session, wp10_session, project, extra_assessments['extra'], kind)
    wp10_session.commit()
