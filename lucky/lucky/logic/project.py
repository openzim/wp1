import logging
import re

from sqlalchemy import or_

from lucky.conf import get_conf
from lucky.constants import AssessmentKind, CATEGORY_NS_INT, GLOBAL_TIMESTAMP
from lucky.logic import page as logic_page, util as logic_util, rating as logic_rating
from lucky.logic.api import project as api_project
from lucky.models.wp10.category import Category
from lucky.models.wp10.project import Project
from lucky.models.wp10.rating import Rating

logger = logging.getLogger(__name__)

config = get_conf()
CLASS = config['CLASS']
QUALITY = config['QUALITY']
IMPORTANCE = config['IMPORTANCE']
NOT_A_CLASS = config['NOT_A_CLASS']
UNASSESSED_CLASS = config['UNASSESSED_CLASS']
UNKNOWN_CLASS = config['UNKNOWN_CLASS']

RE_INDICATOR = re.compile(b'([A-Za-z]+)[ _-]')

def update_category(
    wp10_session, project, page, extra, kind, rating_to_category):
  replaces = None
  extra_category = extra.get(page.title)
  if extra_category is not None:
    rating = extra_category['title']
    ranking = extra_category['ranking']
    if kind == AssessmentKind.QUALITY:
      replaces = extra_category['replaces']
  else:
    md = RE_INDICATOR.search(page.title)
    if not md:
      logger.debug('Skipping page with no class match: %s',
                   page.title.decode('utf-8'))
      return

    rating = ('%s-%s' % (md.group(1).decode('utf-8'), CLASS))
    if kind == AssessmentKind.QUALITY:
      rating_map = QUALITY
    else:
      rating_map = IMPORTANCE

    if rating not in rating_map:
      logger.debug('Skipping page with indicator not in mapping: %s | %s',
                   page.title.decode('utf-8'), rating)
      return
    ranking = rating_map[rating]

  rating_to_category[rating] = page.title
  if replaces is None:
    replaces = rating

  category = Category(
    project=project.project, type=kind.value.encode('utf-8'),
    rating=rating.encode('utf-8'), category=page.title, ranking=ranking,
    replacement=replaces.encode('utf-8'))
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
    if found_page or category_name_main == category_name_alt:
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
      old_rating = old_ratings.get(article_ref)
      old_rating_value = None

      current_rating = Rating(project=project.project, namespace=namespace,
                              article=page.title, score=0)
      if kind == AssessmentKind.QUALITY:
        current_rating.quality = rating.encode('utf-8')
        current_rating.set_quality_timestamp_dt(page.timestamp)
        if old_rating:
          old_rating_value = old_rating.quality
      elif kind == AssessmentKind.IMPORTANCE:
        current_rating.importance = rating.encode('utf-8')
        current_rating.set_importance_timestamp_dt(page.timestamp)
        if old_rating:
          old_rating_value = old_rating.importance

      if old_rating_value is None:
        old_rating_value = NOT_A_CLASS.encode('utf-8')

      # If the article is new, or if the rating doesn't match, save the rating.
      if (article_ref not in old_ratings or
          old_rating_value != rating):
        current_rating = wp10_session.merge(current_rating)
        wp10_session.add(current_rating)
        logic_rating.add_log_for_rating(
          wp10_session, current_rating, kind, old_rating_value)
    wp10_session.commit()

  logging.debug('Looking for unseen articles')
  for ref, old_rating in old_ratings.items():
    if ref in seen:
      continue

    if ((kind == AssessmentKind.QUALITY and
         old_rating.quality == NOT_A_CLASS) or
        (kind == AssessmentKind.IMPORTANCE and
         (old_rating.importance == NOT_A_CLASS
          or old_rating.importance == ''
          or old_rating.importance is None))):
      continue

    logging.debug('Processing unseen article %s', ref.decode('utf-8'))
    ns, title = ref.decode('utf-8').split(':')
    ns = int(ns.encode('utf-8'))
    title = title.encode('utf-8')

    move_data = logic_page.get_move_data(
      wp10_session, ns, title, project.timestamp_dt)
    if move_data is not None:
      logic_page.update_page_moved(
        wp10_session, project, ns, title, move_data['dest_ns'],
        move_data['dest_title'], move_data['timestamp_dt'])
      
    current_rating = Rating(
      project=project.project, namespace=ns, article=title, score=0)
    if kind == AssessmentKind.QUALITY:
      current_rating.quality = NOT_A_CLASS.encode('utf-8')
      old_rating_value = old_rating.quality
    elif kind == AssessmentKind.IMPORTANCE:
      current_rating.importance = NOT_A_CLASS.encode('utf-8')
      old_rating_value = old_rating.importance

    current_rating = wp10_session.merge(current_rating)
    wp10_session.add(current_rating)
    logic_rating.add_log_for_rating(
      wp10_session, current_rating, kind, old_rating_value)
  wp10_session.commit()

def cleanup_project(wp10_session, project):
  not_a_class_db = NOT_A_CLASS.encode('utf-8')
  # If both quality and importance are 'NotA-Class', that means the article
  # was once rated but isn't any more, so we delete the row
  count = wp10_session.query(Rating).filter(
    Rating.project == project.project).filter(
    or_(Rating.quality == not_a_class_db, Rating.quality == None)).filter(
    or_(Rating.importance == not_a_class_db,
        Rating.importance == None)).delete()
  logger.info('Deleted %s ratings that were empty from project: %s',
              count, project.project.decode('utf-8'))

  # It's possible for the quality to be NULL if the article has a 
  # rated importance but no rated quality (not even Unassessed-Class).
  # This will always happen if the article has a quality rating that the 
  # bot doesn't recognize. Change the NULL to sentinel value.
  count = wp10_session.query(Rating).filter(
    Rating.project == project.project).filter(
    Rating.quality == None).update({
      Rating.quality: not_a_class_db,
      Rating.quality_timestamp: Rating.importance_timestamp
    })
  logger.info('Updated %s ratings, quality == NotAClass from project: %s',
              count, project.project.decode('utf-8'))

  # Finally, if a quality is assigned but not an importance, it is
  # possible for the importance field to be null. Set it to 
  # $NotAClass in this case.
  count = wp10_session.query(Rating).filter(
    Rating.project == project.project).filter(
    Rating.importance == None).update({
      Rating.importance: not_a_class_db,
      Rating.importance_timestamp: Rating.quality_timestamp
    })
  logger.info('Updated %s ratings, importance == NotAClass from project: %s',
        count, project.project.decode('utf-8'))

def update_project_record(wp10_session, project, metadata):
  not_a_class_db = NOT_A_CLASS.encode('utf-8')
  unassessed_db = UNASSESSED_CLASS.encode('utf-8')
  unknown_db = UNKNOWN_CLASS.encode('utf-8')

  num_ratings = wp10_session.query(Rating).filter(
    Rating.project == project.project).count()

  num_unassessed_quality = wp10_session.query(Rating).filter(
    or_(Rating.quality == not_a_class_db,
        Rating.quality == unassessed_db)).count()
  quality_count = num_ratings - num_unassessed_quality

  num_unassessed_importance = wp10_session.query(Rating).filter(
    or_(Rating.importance == not_a_class_db,
        Rating.importance == unassessed_db,
        Rating.importance == unknown_db)).count()
  importance_count = num_ratings - num_unassessed_importance

  # Okay, update the fields of the project, warning if we're setting NULLs.
  project_display = project.project.decode('utf-8')
  project.timestamp = GLOBAL_TIMESTAMP
  wikipage = metadata.get('homepage')
  if wikipage is None:
    logger.warning('Setting NULL wikipage for project: %s', project_display)
  else:
    project.wikipage = wikipage.encode('utf-8')
  parent = metadata.get('parent')
  if parent is None:
    logger.warning('Setting NULL parent for project: %s', project_display)
  else:
    project.parent = parent.encode('utf-8')
  shortname = metadata.get('shortname')
  if shortname is None:
    logger.warning('Setting NULL shortname for project: %s', project_display)
  else:
    project.shortname = shortname.encode('utf-8')
  project.count = num_ratings
  project.qcount = quality_count
  project.icount = importance_count

  wp10_session.add(project)

def update_project(wiki_session, wp10_session, project):
  extra_assessments = api_project.get_extra_assessments(project.project)
  timestamp = project.timestamp

  for kind in (AssessmentKind.QUALITY, AssessmentKind.IMPORTANCE):
    logger.debug('Updating %s assessments by %s',
                 project.project.decode('utf-8'), kind)
    update_project_assessments(
      wiki_session, wp10_session, project, extra_assessments['extra'], kind)
    wp10_session.commit()

  cleanup_project(wp10_session, project)
  wp10_session.commit()

  update_project_record(wp10_session, project, extra_assessments)
