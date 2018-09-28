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
NOT_A_CLASS = config['NOT_A_CLASS']

RE_INDICATOR = re.compile(b'([A-Za-z]+)[ _-]')

def update_category(
    wp10_session, project, page, extra, kind, rating_to_category):
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

  rating_to_category[rating] = page.title

  category = Category(
    project=project.project, type=kind.value.encode('utf-8'),
    rating=rating.encode('utf-8'), category=page.title, ranking=ranking,
    replacement=rating.encode('utf-8'))
  # If there is an existing category, merge in our changes
  category = wp10_session.merge(category)
  wp10_session.add(category)


def update_project_categories_by_kind(
    wiki_session, wp10_session, project, extra, kind):
  logging.info('Updating project categories for %s', project.project)
  rating_to_category = {}
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
        wp10_session, project, page, extra, kind, rating_to_category)

    # There might not be any pages listed "by importance" so we have to check
    # the alternate name ("by priority"), unless we already found pages.
    if found_page:
      break

  return rating_to_category

def update_project_assessments(
    wiki_session, wp10_session, project, extra_assessments, kind):
  if kind not in (AssessmentKind.QUALITY, AssessmentKind.IMPORTANCE):
    raise ValueError('Parameter "kind" was not one of QUALITY or IMPORTANCE')

  logging.info('Updating project %s assessments for %s', kind, project.project)
  old_ratings = {}
  for rating in wp10_session.query(Rating).filter(
      Rating.project == project.project):
    rating_ref = str(rating.namespace).encode('utf-8') + b':' + rating.article
    old_ratings[rating_ref] = rating

  seen = set()
  moved = set()

  rating_to_category = update_project_categories_by_kind(
    wiki_session, wp10_session, project, extra_assessments, kind)

  for rating, category in rating_to_category.items():
    logging.info('Fetching article list for %s' % category)
    count = 0
    for page in logic_page.get_pages_by_category(wiki_session, category):
      # Talk pages are tagged, we want the NS of the article itself.
      count += 1
      namespace = page.namespace - 1
      if not logic_util.is_namespace_acceptable(namespace):
        logging.debug('Skipping %s with namespace=%s', page.title, namespace)
        continue

      article_ref = str(namespace).encode('utf-8') + b':' +  page.title
      seen.add(article_ref)

      current_rating = Rating(project=project.project, namespace=namespace,
                              article=page.title, score=0)
      if kind == AssessmentKind.QUALITY:
        current_rating.quality = rating.encode('utf-8')
        current_rating.set_quality_timestamp_dt(page.timestamp)
      elif kind == AssessmentKind.IMPORTANCE:
        current_rating.importance = rating.encode('utf-8')
        current_rating.set_importance_timestamp_dt(page.timestamp)

      # If the article is new, or if the rating doesn't match, save the rating.
      if (article_ref not in old_ratings or
          (kind == AssessmentKind.QUALITY and
          old_ratings[article_ref].quality != rating) or (
          kind == AssessmentKind.IMPORTANCE and
          old_ratings[article_ref].importance != rating)):
        # TODO: update logging table
        current_rating = wp10_session.merge(current_rating)
        wp10_session.add(current_rating)
    wp10_session.commit()

  logging.debug('Looking for unseen articles')
  for ref, old_rating in old_ratings.items():
    # TODO: Figure out how to process unseen articles without hanging forever
    # on the logging table lookup
    continue

    if ref in seen:
      continue

    if ((kind == AssessmentKind.QUALITY and
         old_rating.quality == NOT_A_CLASS) or
        (kind == AssessmentKind.IMPORTANCE and
         old_rating.importance == NOT_A_CLASS or old_rating.importance == '')):
      continue

    logging.debug('Processing unseen article %s', ref)
    ns, title = ref.decode('utf-8').split(':')
    ns = ns.encode('utf-8')
    title = title.encode('utf-8')

    move_data = logic_page.get_move_data(
      wiki_session, wp10_session, ns, title, project.timestamp)

    if move_data is not None:
      pass
      # TODO: Update move table
      
    current_rating = Rating(
      project=project.project, namespace=ns, article=title, score=0)
    if kind == AssessmentKind.QUALITY:
      current_rating.quality = NOT_A_CLASS.encode('utf-8')
    elif kind == AssessmentKind.IMPORTANCE:
      current_rating.importance = NOT_A_CLASS.encode('utf-8')
    current_rating = wp10_session.merge(current_rating)
    wp10_session.add(current_rating)
  wp10_session.commit()

def update_project(wiki_session, wp10_session, project):
  extra_assessments = api_project.get_extra_assessments(project.project)
  timestamp = project.timestamp

  for kind in (AssessmentKind.QUALITY, AssessmentKind.IMPORTANCE):
    logger.debug('Updating %s assessments by %s',
                 project.project.decode('utf-8'), kind)
    update_project_assessments(
      wiki_session, wp10_session, project, extra_assessments['extra'], kind)
    wp10_session.commit()
