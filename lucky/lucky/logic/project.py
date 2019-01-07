import logging
import math
import re

from sqlalchemy import or_

from lucky.conf import get_conf
from lucky.constants import AssessmentKind, CATEGORY_NS_INT, GLOBAL_TIMESTAMP, GLOBAL_TIMESTAMP_WIKI
from lucky.logic import page as logic_page, util as logic_util, rating as logic_rating, category as logic_category
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


def insert_or_update(wp10db, project):
  raise NotImplementedError('Need to convert to db access')


def update_category(wp10db, project, page, extra, kind, rating_to_category):
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
  # If there is an existing category, merge in our changes.
  logic_category.insert_or_update(wp10db, category)


def update_project_categories_by_kind(
    wikidb, wp10db, project, extra, kind):
  logging.info('Updating project categories for %s', project.project)
  rating_to_category = {}
  category_name_main = logic_util.category_for_project_by_kind(
    project.project, kind, category_prefix=False)
  category_name_alt = logic_util.category_for_project_by_kind(
    project.project, kind, category_prefix=False, use_alt=True)

  found_page = False
  for category_name in (category_name_main, category_name_alt):
    for page in logic_page.get_pages_by_category(
        wikidb, category_name, ns=CATEGORY_NS_INT):
      found_page = True
      update_category(wp10db, project, page, extra, kind, rating_to_category)

    # There might not be any pages listed "by importance" so we have to check
    # the alternate name ("by priority"), unless we already found pages.
    if found_page or category_name_main == category_name_alt:
      break

  return rating_to_category


def update_project_assessments(
    wikidb, wp10db, project, extra_assessments, kind):
  if kind not in (AssessmentKind.QUALITY, AssessmentKind.IMPORTANCE):
    raise ValueError('Parameter "kind" was not one of QUALITY or IMPORTANCE')

  logging.info('Updating project %s assessments for %s', kind, project.project)
  old_ratings = {}
  for rating in rating.get_project_ratings(wp10db, project.project):
    rating_ref = str(rating.namespace).encode('utf-8') + b':' + rating.article
    old_ratings[rating_ref] = rating

  seen = set()
  rating_to_category = update_project_categories_by_kind(
    wikidb, wp10db, project, extra_assessments, kind)

  for current_rating, category in rating_to_category.items():
    logging.info('Fetching article list for %r' % category.decode('utf-8'))
    for page in logic_page.get_pages_by_category(wikidb, category):
      # Talk pages are tagged, we want the NS of the article itself.
      namespace = page.namespace - 1
      if not logic_util.is_namespace_acceptable(namespace):
        logging.debug('Skipping %s with namespace=%s', page.title, namespace)
        continue

      article_ref = str(namespace).encode('utf-8') + b':' +  page.title
      seen.add(article_ref)
      old_rating = old_ratings.get(article_ref)
      old_rating_value = None

      if old_rating:
        rating = old_rating
        if kind == AssessmentKind.QUALITY:
          old_rating_value = rating.quality
        elif kind == AssessmentKind.IMPORTANCE:
          old_rating_value = rating.importance
      else:
        rating = Rating(project=project.project, namespace=namespace,
                              article=page.title, score=0)
        old_rating_value = NOT_A_CLASS.encode('utf-8')

      if kind == AssessmentKind.QUALITY:
        rating.quality = current_rating.encode('utf-8')
        rating.set_quality_timestamp_dt(page.timestamp)
      elif kind == AssessmentKind.IMPORTANCE:
        rating.importance = current_rating.encode('utf-8')
        rating.set_importance_timestamp_dt(page.timestamp)

      if (article_ref in old_ratings and old_rating_value != rating):
        # If the article doesn't match its rating, update the logging table.
        logic_rating.add_log_for_rating(wp10db, rating, kind, old_rating_value)
      else:
        # Add the newly created rating.
        log_rating.insert(wp10db, rating)

  logging.debug('Looking for unseen articles')
  n = 0
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
    ns, title = ref.decode('utf-8').split(':', 1)
    ns = int(ns.encode('utf-8'))
    title = title.encode('utf-8')

    move_data = logic_page.get_move_data(
      wp10db, ns, title, project.timestamp_dt)
    if move_data is not None:
      logic_page.update_page_moved(
        wp10db, project, ns, title, move_data['dest_ns'],
        move_data['dest_title'], move_data['timestamp_dt'])

    rating = Rating(
      project=project.project, namespace=ns, article=title, score=0)
    if kind == AssessmentKind.QUALITY:
      rating.quality = NOT_A_CLASS.encode('utf-8')
      old_rating_value = old_rating.quality
      if move_data:
        current_rating.set_quality_timestamp_dt(move_data['timestamp_dt'])
      else:
        current_rating.quality_timestamp = GLOBAL_TIMESTAMP_WIKI
    elif kind == AssessmentKind.IMPORTANCE:
      rating.importance = NOT_A_CLASS.encode('utf-8')
      old_rating_value = old_rating.importance
      if move_data:
        rating.set_importance_timestamp_dt(move_data['timestamp_dt'])
      else:
        rating.importance_timestamp = GLOBAL_TIMESTAMP_WIKI

    logic_rating.insert_or_update(rating)
    logic_rating.add_log_for_rating(wp10db, rating, kind, old_rating_value)


def cleanup_project(wp10db, project):
  not_a_class_db = NOT_A_CLASS.encode('utf-8')
  # If both quality and importance are 'NotA-Class', that means the article
  # was once rated but isn't any more, so we delete the row
  count = logic_rating.delete_empty_for_project(wp10db, project.project)

  # count = wp10_session.query(Rating).filter(
  #   Rating.project == project.project).filter(
  #   or_(Rating.quality == not_a_class_db, Rating.quality == None)).filter(
  #   or_(Rating.importance == not_a_class_db,
  #       Rating.importance == None)).delete()
  logger.info('Deleted %s ratings that were empty from project: %s',
              count, project.project.decode('utf-8'))

  # It's possible for the quality to be NULL if the article has a 
  # rated importance but no rated quality (not even Unassessed-Class).
  # This will always happen if the article has a quality rating that the 
  # bot doesn't recognize. Change the NULL to sentinel value.
  count = logic_rating.update_null_ratings_for_project(
    wp10db, project.project, kind=AssessmentKind.QUALITY)

  # count = wp10_session.query(Rating).filter(
  #   Rating.project == project.project).filter(
  #   Rating.quality == None).update({
  #     Rating.quality: not_a_class_db,
  #     Rating.quality_timestamp: Rating.importance_timestamp
  #   })
  logger.info('Updated %s ratings, quality == NotAClass from project: %s',
              count, project.project.decode('utf-8'))

  # Finally, if a quality is assigned but not an importance, it is
  # possible for the importance field to be null. Set it to 
  # $NotAClass in this case.
  count = logic_rating.update_null_ratings_for_project(
    wp10db, project.project, kind=AssessmentKind.IMPORTANCE)

  # count = wp10_session.query(Rating).filter(
  #   Rating.project == project.project).filter(
  #   Rating.importance == None).update({
  #     Rating.importance: not_a_class_db,
  #     Rating.importance_timestamp: Rating.quality_timestamp
  #   })
  logger.info('Updated %s ratings, importance == NotAClass from project: %s',
        count, project.project.decode('utf-8'))


def update_project_record(wp10db, project, metadata):
  project_display = project.project.decode('utf-8')
  logging.info('Updating project record: %r', project_display)

  not_a_class_db = NOT_A_CLASS.encode('utf-8')
  unassessed_db = UNASSESSED_CLASS.encode('utf-8')
  unknown_db = UNKNOWN_CLASS.encode('utf-8')

  num_ratings = logic_rating.count_for_project(wp10db, project.project)

  num_unassessed_quality = logic_rating.count_unassessed_for_project(
    wp10db, project.project, AssessmentKind.QUALITY)
  quality_count = num_ratings - num_unassessed_quality

  num_unassessed_importance = logic_rating.count_unassessed_for_project(
    wp10db, project.project, AssessmentKind.IMPORTANCE)
  importance_count = num_ratings - num_unassessed_importance

  # Okay, update the fields of the project, warning if we're setting NULLs.
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
  project.scope = 0
  project.upload_timestamp = b'00000000000000'

  insert_or_update(wp10db, project)

def update_articles_table(wp10_session, project):
  # This is a fairly complex query, but it performs relatively well. It would
  # be complex to translate it to the ORM layer and perserve the nuance of what
  # to do when certain values are NULL, etc. So we'll just copy it from the old
  # codebase and execute it.

  # Call to this method is currently commented out
  # wp10_session.execute('''
  #   REPLACE INTO lucky_global_articles
  #   SELECT art, max(qrating), max(irating), max(score)
  #   FROM
  #   ( SELECT art, qrating, irating, score
  #     FROM
  #       (SELECT a_article as art, a_quality as qrating,
  #               a_importance as irating, a_score as score
  #          FROM global_articles
  #          JOIN ratings 
  #              ON r_namespace = 0 AND r_project = :project AND
  #                 a_article = r_article
  #       ) AS tableone
  #     UNION
  #       (SELECT r_article as art, qual.gr_ranking as qrating,
  #               imp.gr_ranking as irating, r_score as score
  #         FROM ratings
  #         JOIN categories as ci
  #           ON r_project = ci.c_project AND ci.c_type = 'importance' AND
  #              r_importance = ci.c_rating
  #         JOIN categories as cq
  #           ON r_project = cq.c_project AND
  #              cq.c_type = 'quality' AND r_quality = cq.c_rating
  #         JOIN global_rankings AS qual
  #           ON qual.gr_type = 'quality' AND qual.gr_rating = cq.c_replacement
  #         JOIN  global_rankings AS imp
  #           ON imp.gr_type = 'importance' AND imp.gr_rating = ci.c_replacement
  #       WHERE r_namespace = 0 and r_project = :project )
  #   ) as tabletwo
  #   GROUP BY art
  # ''', {'project': project.project})
  pass

def update_project(wikidb, wp10db, project):
  extra_assessments = api_project.get_extra_assessments(project.project)
  timestamp = project.timestamp

  for kind in (AssessmentKind.QUALITY, AssessmentKind.IMPORTANCE):
    logger.debug('Updating %s assessments by %s',
                 project.project.decode('utf-8'), kind)
    update_project_assessments(
      wikidb, wp10db, project, extra_assessments['extra'], kind)

  cleanup_project(wp10db, project)

  update_project_record(wp10db, project, extra_assessments)

  ## This is where the old code would update the project scores. However, since
  ## we don't have reliable selection_data at the moment, and we're not sure if
  ## the score metrics will be changing, skip it for now.
  # update_project_scores(wp10_session, project)

  update_articles_table(wp10db, project)
