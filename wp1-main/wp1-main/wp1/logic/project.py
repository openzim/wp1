from collections import defaultdict
import logging
import math
import re
import time

import attr

from wp1 import api
from wp1.conf import get_conf
from wp1.constants import AssessmentKind, CATEGORY_NS_INT, GLOBAL_TIMESTAMP, GLOBAL_TIMESTAMP_WIKI, MAX_ARTICLES_BEFORE_COMMIT
from wp1.logic import page as logic_page, util as logic_util, rating as logic_rating, category as logic_category
from wp1.logic.api import project as api_project
from wp1.models.wiki.page import Page
from wp1.models.wp10.category import Category
from wp1.models.wp10.project import Project
from wp1.models.wp10.rating import Rating
from wp1.redis_db import connect as redis_connect
from wp1 import tables
from wp1.wp10_db import connect as wp10_connect
from wp1.wiki_db import connect as wiki_connect

logger = logging.getLogger(__name__)

config = get_conf()
ARTICLES_LABEL = config['ARTICLES_LABEL'].encode('utf-8')
BY_QUALITY = config['BY_QUALITY'].encode('utf-8')
BY_IMPORTANCE = config['BY_IMPORTANCE'].encode('utf-8')
CATEGORY_NS = config['CATEGORY_NS'].encode('utf-8')
CLASS = config['CLASS']
IMPORTANCE = config['IMPORTANCE']
NOT_A_CLASS = config['NOT_A_CLASS']
QUALITY = config['QUALITY']
ROOT_CATEGORY = config['ROOT_CATEGORY'].encode('utf-8')

RE_INDICATOR = re.compile(b'([A-Za-z]+)[ _-]')
RE_REJECT_GENERIC = re.compile(ARTICLES_LABEL + b'_' + BY_QUALITY, re.I)


def count_projects(wp10db):
  with wp10db.cursor() as cursor:
    cursor.execute('SELECT COUNT(*) AS count FROM projects')
    res = cursor.fetchone()

  return res and res['count']


def update_global_project_count():
  wp10db = wp10_connect()
  try:
    logger.info('Querying for number of projects')

    count = count_projects(wp10db)

    logger.info('Found %s projects, updating wiki', count)
    page = api.get_page('User:WP 1.0 bot/Data/Count')
    api.save_page(page, '%s\n' % count, 'Updating count: %s projects' % count)
  finally:
    wp10db.close()


def update_project_by_name(project_name, track_progress=False):
  wp10db = wp10_connect()
  wikidb = wiki_connect()
  redis = redis_connect()

  logging.basicConfig(level=logging.INFO)
  logging.getLogger('mwclient').setLevel(logging.CRITICAL)
  logging.getLogger('urllib3').setLevel(logging.CRITICAL)
  logging.getLogger('requests_oauthlib').setLevel(logging.CRITICAL)
  logging.getLogger('oauthlib').setLevel(logging.CRITICAL)

  try:
    project = get_project_by_name(wp10db, project_name)
    if not project:
      project = Project(p_project=project_name,
                        p_timestamp=GLOBAL_TIMESTAMP_WIKI)
    update_project(wikidb,
                   wp10db,
                   project,
                   redis=redis,
                   track_progress=track_progress)

    if track_progress:
      redis.expire(_project_progress_key(project_name), 600)
  finally:
    wp10db.close()
    wikidb.close()


def update_global_articles_for_project_name(wp10db, project_name):
  logger.info('Executing global update for: %s' % project_name.decode('utf-8'))
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''
        REPLACE INTO global_articles
        SELECT art, max(qrating), max(irating), max(score)
        FROM (
          SELECT art, qrating, irating, score FROM
            (SELECT a_article AS art, a_quality AS qrating,
                    a_importance AS irating, a_score AS score
             FROM global_articles
             JOIN ratings
               ON r_namespace = 0 AND r_project = %(project)s AND
                  a_article = r_article
            ) as t1
            UNION
            (SELECT r_article AS art, qual.gr_ranking AS qrating,
                    imp.gr_ranking AS irating, r_score AS score
             FROM ratings
             JOIN categories AS ci
               ON r_project = ci.c_project AND ci.c_type = 'importance' AND
                  r_importance = ci.c_rating
             JOIN categories AS cq
               ON r_project = cq.c_project AND
                  cq.c_type = 'quality' AND r_quality = cq.c_rating
             JOIN global_rankings AS qual
               ON qual.gr_type = 'quality' AND qual.gr_rating = cq.c_replacement
             JOIN global_rankings AS imp
               ON imp.gr_type = 'importance' AND
                  imp.gr_rating = ci.c_replacement
             WHERE r_namespace = 0 AND r_project = %(project)s)
        ) as t2
        GROUP BY art
    ''', {'project': project_name})
  wp10db.commit()


def project_names_to_update(wikidb):
  projects_in_root = logic_page.get_pages_by_category(wikidb, ROOT_CATEGORY,
                                                      CATEGORY_NS_INT)
  # List instead of iterate because the query will be reused in the processing
  # steps and if we don't exhaust it now, it will get truncated.
  for category_page in list(projects_in_root):
    if BY_QUALITY not in category_page.page_title:
      logger.info('Skipping %s -- it does not have quality in title' %
                  category_page.page_title.decode('utf-8'))
      continue

    if RE_REJECT_GENERIC.match(category_page.page_title):
      logger.info('Skipping %r -- it is a generic "articles by quality"' %
                  category_page)
      continue

    yield category_page.base_title


def list_all_projects(wp10db):
  with wp10db.cursor() as cursor:
    cursor.execute('''
      SELECT p_project, p_timestamp, p_count, p_qcount, p_icount FROM projects
      ''')
    return [Project(**db_project) for db_project in cursor.fetchall()]


def insert_or_update(wp10db, project):
  with wp10db.cursor() as cursor:
    logger.debug('Updating project: %r', project)
    cursor.execute(
        '''
        UPDATE projects
        SET p_timestamp=%(p_timestamp)s, p_wikipage=%(p_wikipage)s,
            p_parent=%(p_parent)s, p_shortname=%(p_shortname)s,
            p_count=%(p_count)s, p_qcount=%(p_qcount)s, p_icount=%(p_icount)s,
            p_upload_timestamp=%(p_upload_timestamp)s, p_scope=%(p_scope)s
        WHERE p_project=%(p_project)s
    ''', attr.asdict(project))
    if cursor.rowcount == 0:
      logger.debug('No project to update, inserting')
      cursor.execute(
          '''
          INSERT INTO projects
            (p_project, p_timestamp, p_wikipage, p_parent, p_shortname, p_count,
             p_qcount, p_icount, p_upload_timestamp, p_scope)
          VALUES
            (%(p_project)s, %(p_timestamp)s, %(p_wikipage)s, %(p_parent)s,
             %(p_shortname)s, %(p_count)s, %(p_qcount)s, %(p_icount)s,
             %(p_upload_timestamp)s, %(p_scope)s)
          ON DUPLICATE KEY UPDATE p_timestamp = %(p_timestamp)s
      ''', attr.asdict(project))
  wp10db.commit()


def get_project_by_name(wp10db, project_name):
  with wp10db.cursor() as cursor:
    cursor.execute('SELECT * FROM projects WHERE p_project=%(p_project)s',
                   {'p_project': project_name})
    db_project = cursor.fetchone()
    if db_project is None:
      return None
    return Project(**db_project)


def update_category(wp10db, project, page, extra, kind, rating_to_category):
  replaces = None
  extra_category = extra.get('extra', {}).get(page.page_title.decode('utf-8'))
  if extra_category is not None:
    rating = extra_category.get('title')
    ranking = extra_category.get('ranking')
    if rating is None or ranking is None:
      logger.warning(
          'Skipping extra category with missing "title" or "ranking" field: %s',
          extra_category)
      return

    try:
      ranking = int(ranking)
    except ValueError:
      logging.warning(
          'Could not cast "ranking" field for extra category to int: %s | %s',
          extra_category, ranking)
      return

    if kind == AssessmentKind.QUALITY:
      replaces = extra_category.get('replaces')
  else:
    md = RE_INDICATOR.search(page.page_title)
    if not md:
      logger.debug('Skipping page with no class match: %s',
                   page.page_title.decode('utf-8'))
      return

    rating = ('%s-%s' % (md.group(1).decode('utf-8'), CLASS))
    if kind == AssessmentKind.QUALITY:
      rating_map = QUALITY
    else:
      rating_map = IMPORTANCE

    if rating not in rating_map:
      logger.debug('Skipping page with indicator not in mapping: %s | %s',
                   page.page_title.decode('utf-8'), rating)
      return
    ranking = rating_map[rating]

  rating_to_category[rating] = (page.page_title, ranking)
  if replaces is None:
    replaces = rating

  category = Category(c_project=project.p_project,
                      c_type=kind.value.encode('utf-8'),
                      c_rating=rating.encode('utf-8'),
                      c_category=page.page_title,
                      c_ranking=ranking,
                      c_replacement=replaces.encode('utf-8'))

  # If there is an existing category, merge in our changes.
  logic_category.insert_or_update(wp10db, category)


def create_not_a_class_categories(wp10db, project):
  for kind in (AssessmentKind.QUALITY, AssessmentKind.IMPORTANCE):
    rating = NOT_A_CLASS

    if kind == AssessmentKind.QUALITY:
      rating_map = QUALITY
    else:
      rating_map = IMPORTANCE
    ranking = rating_map[rating]

    category = Category(c_project=project.p_project,
                        c_type=kind.value.encode('utf-8'),
                        c_rating=rating.encode('utf-8'),
                        c_category=b'',
                        c_ranking=ranking,
                        c_replacement=b'Unknown-Class')

    logic_category.insert_or_update(wp10db, category)


def update_project_categories_by_kind(wikidb, wp10db, project, extra, kind):
  logger.info('Updating project categories for %s', project.p_project)
  rating_to_category = {}
  category_name_main = logic_util.category_for_project_by_kind(
      project.p_project, kind, category_prefix=False)
  category_name_alt = logic_util.category_for_project_by_kind(
      project.p_project, kind, category_prefix=False, use_alt=True)

  found_page = False
  for category_name in (category_name_main, category_name_alt):
    for page in logic_page.get_pages_by_category(wikidb,
                                                 category_name,
                                                 ns=CATEGORY_NS_INT):
      found_page = True
      update_category(wp10db, project, page, extra, kind, rating_to_category)

    # There might not be any pages listed "by importance" so we have to check
    # the alternate name ("by priority"), unless we already found pages.
    if found_page:
      break

  # There is no wiki category for NotA-Class, but we need to make categories
  # for it so that it shows up in the assessment table.
  create_not_a_class_categories(wp10db, project)

  return rating_to_category


def _project_progress_key(project_name):
  return b'progress:%s' % project_name


def clear_project_progress(redis, project_name):
  key = _project_progress_key(project_name)
  redis.delete(key)


def get_project_progress(redis, project_name):
  key = _project_progress_key(project_name)

  if not redis.exists(key):
    return None, None

  return redis.hmget(key, ('progress', 'work'))


def count_initial_work(redis, wp10db, project_name):
  if redis is None:
    logger.error(
        'Attempt to track progress without specifying a Redis instance')
    return

  count = logic_rating.get_all_ratings_count_for_project(wp10db, project_name)
  # Not all articles have both quality and importance.
  work = int(count * 1.9)

  key = _project_progress_key(project_name)
  redis.hset(key, 'work', work)
  redis.hset(key, 'progress', 0)


def increment_progress_count(redis, project_name):
  if redis is None:
    return

  key = _project_progress_key(project_name)
  redis.hincrby(key, 'progress', 1)


def update_project_assessments(wikidb,
                               wp10db,
                               project,
                               extra_assessments,
                               redis=None,
                               track_progress=False):
  old_ratings = {}
  for rating in logic_rating.get_project_ratings(wp10db, project.p_project):
    rating_ref = (str(rating.r_namespace).encode('utf-8') + b':' +
                  rating.r_article)
    old_ratings[rating_ref] = rating

  if track_progress:
    count_initial_work(redis, wp10db, project.p_project)

  seen = set()
  for kind in (AssessmentKind.QUALITY, AssessmentKind.IMPORTANCE):
    logger.debug('Updating %s assessments by %s',
                 project.p_project.decode('utf-8'), kind)
    new_ratings, rating_to_category = update_project_assessments_by_kind(
        wikidb,
        wp10db,
        project,
        extra_assessments,
        kind,
        old_ratings,
        seen,
        redis=redis,
        track_progress=track_progress)
    store_new_ratings(wp10db, new_ratings, old_ratings, rating_to_category)

  process_unseen_articles(wikidb, wp10db, project, old_ratings, seen)


def update_project_assessments_by_kind(wikidb,
                                       wp10db,
                                       project,
                                       extra_assessments,
                                       kind,
                                       old_ratings,
                                       seen,
                                       redis=None,
                                       track_progress=False):
  if kind not in (AssessmentKind.QUALITY, AssessmentKind.IMPORTANCE):
    raise ValueError('Parameter "kind" was not one of QUALITY or IMPORTANCE')

  logger.info('Updating project %s assessments for %s', kind, project.p_project)
  rating_to_category = update_project_categories_by_kind(
      wikidb, wp10db, project, extra_assessments, kind)

  n = 0
  new_ratings = defaultdict(list)
  for current_rating, (category, ranking) in rating_to_category.items():
    logger.info('Fetching article list for %r' % category.decode('utf-8'))
    current_rating = current_rating.encode('utf-8')

    for page in logic_page.get_pages_by_category(wikidb, category):
      # Talk pages are tagged, we want the NS of the article itself.
      namespace = page.page_namespace - 1
      if not logic_util.is_namespace_acceptable(namespace):
        logger.debug('Skipping %s with namespace=%s', page.page_title,
                     namespace)
        continue

      article_ref = str(namespace).encode('utf-8') + b':' + page.page_title
      seen.add(article_ref)

      old_rating = old_ratings.get(article_ref)
      old_rating_value = None

      if old_rating:
        rating = Rating(**attr.asdict(old_rating))
        if kind == AssessmentKind.QUALITY:
          old_rating_value = rating.r_quality
        elif kind == AssessmentKind.IMPORTANCE:
          old_rating_value = rating.r_importance
      else:
        rating = Rating(r_project=project.p_project,
                        r_namespace=namespace,
                        r_article=page.page_title,
                        r_score=0)
        old_rating_value = NOT_A_CLASS.encode('utf-8')

      if kind == AssessmentKind.QUALITY:
        rating.r_quality = current_rating
        rating.set_quality_timestamp_dt(page.cl_timestamp)
      elif kind == AssessmentKind.IMPORTANCE:
        rating.r_importance = current_rating
        rating.set_importance_timestamp_dt(page.cl_timestamp)

      new_ratings[article_ref].append((rating, kind, old_rating_value))
      n += 1
      if n >= MAX_ARTICLES_BEFORE_COMMIT:
        wp10db.ping()
        wp10db.commit()

      if track_progress:
        increment_progress_count(redis, project.p_project)
  logger.info('End, committing db')
  wp10db.ping()
  wp10db.commit()

  return (new_ratings, rating_to_category)


def store_new_ratings(wp10db, new_ratings, old_ratings, rating_to_category):

  def sort_rating_tuples(rating_tuple):
    rating, kind, _ = rating_tuple
    if kind == AssessmentKind.QUALITY:
      return rating_to_category[rating.r_quality.decode('utf-8')][1]  # ranking
    if kind == AssessmentKind.IMPORTANCE:
      return rating_to_category[rating.r_importance.decode('utf-8')][
          1]  # ranking

  for article_ref, ratings_list in new_ratings.items():
    sorted_ratings = sorted(ratings_list, key=sort_rating_tuples, reverse=True)
    rating, kind, old_rating_value = sorted_ratings[0]

    if kind == AssessmentKind.QUALITY:
      rating_changed = rating.r_quality != old_rating_value
    elif kind == AssessmentKind.IMPORTANCE:
      rating_changed = rating.r_importance != old_rating_value

    if article_ref not in old_ratings or rating_changed:
      logic_rating.insert_or_update(wp10db, rating, kind)
      logic_rating.add_log_for_rating(wp10db, rating, kind, old_rating_value)


def process_unseen_articles(wikidb, wp10db, project, old_ratings, seen):
  denom = len(old_ratings.keys())
  ratio = len(seen) / denom if denom != 0 else 'NaN'

  logger.debug('Looking for unseen articles, ratio was: %s', ratio)
  in_seen = 0
  skipped = 0
  processed = 0
  n = 0
  for ref, old_rating in old_ratings.items():
    if ref in seen:
      in_seen += 1
      continue

    # By default, we evaluate both assessment kinds.
    kind = AssessmentKind.BOTH
    if old_rating.r_quality == NOT_A_CLASS or old_rating.r_quality is None:
      # The quality rating is not set, so just evaluate importance
      kind = AssessmentKind.IMPORTANCE
      if (old_rating.r_importance == NOT_A_CLASS or
          old_rating.r_importance is None):
        # The importance rating is also not set, so don't do anything.
        skipped += 1
        continue

    logger.debug('Processing unseen article %s', ref.decode('utf-8'))
    processed += 1
    ns, title = ref.decode('utf-8').split(':', 1)
    ns = int(ns.encode('utf-8'))
    title = title.encode('utf-8')

    move_data = logic_page.get_move_data(wp10db, wikidb, ns, title,
                                         project.timestamp_dt)
    if move_data is not None:
      logic_page.update_page_moved(wp10db, project, ns, title,
                                   move_data['dest_ns'],
                                   move_data['dest_title'],
                                   move_data['timestamp_dt'])

    # Mark this article as having NOT_A_CLASS for it's quality or importance.
    # This probably means the article was deleted, but could in fact mean that
    # we just failed to find its move data. Either way, the new article would
    # have already been picked up by the assessment updater, assuming it was
    # tagged correctly.
    rating = Rating(r_project=project.p_project,
                    r_namespace=ns,
                    r_article=title,
                    r_score=0)
    if kind in (AssessmentKind.QUALITY, AssessmentKind.BOTH):
      rating.quality = NOT_A_CLASS.encode('utf-8')
      if move_data:
        rating.set_quality_timestamp_dt(move_data['timestamp_dt'])
      else:
        rating.r_quality_timestamp = GLOBAL_TIMESTAMP_WIKI
    if kind in (AssessmentKind.IMPORTANCE, AssessmentKind.BOTH):
      rating.importance = NOT_A_CLASS.encode('utf-8')
      if move_data:
        rating.set_importance_timestamp_dt(move_data['timestamp_dt'])
      else:
        rating.r_importance_timestamp = GLOBAL_TIMESTAMP_WIKI

    logic_rating.insert_or_update(wp10db, rating, kind)

    if kind in (AssessmentKind.QUALITY, AssessmentKind.BOTH):
      logic_rating.add_log_for_rating(wp10db, rating, AssessmentKind.QUALITY,
                                      old_rating.r_quality)
    if kind in (AssessmentKind.IMPORTANCE, AssessmentKind.BOTH):
      logic_rating.add_log_for_rating(wp10db, rating, AssessmentKind.IMPORTANCE,
                                      old_rating.r_importance)

    n += 1
    if n >= MAX_ARTICLES_BEFORE_COMMIT:
      wp10db.ping()
      wp10db.commit()
  logger.info('End, committing db')
  wp10db.ping()
  wp10db.commit()

  logger.debug('SEEN REPORT:\nin seen: %s\nskipped: %s\nprocessed: %s', in_seen,
               skipped, processed)


def cleanup_project(wp10db, project):
  # If both quality and importance are 'NotA-Class', that means the article
  # was once rated but isn't any more, so we delete the row
  count = logic_rating.delete_empty_for_project(wp10db, project)
  logger.info('Deleted %s ratings that were empty for project: %s', count,
              project.p_project.decode('utf-8'))

  # It's possible for the quality to be NULL if the article has a
  # rated importance but no rated quality (not even Unassessed-Class).
  # This will always happen if the article has a quality rating that the
  # bot doesn't recognize. Change the NULL to sentinel value.
  count = logic_rating.update_null_quality_for_project(wp10db, project)
  logger.info('Updated %s ratings, quality == NotAClass for project: %s', count,
              project.p_project.decode('utf-8'))

  # Finally, if a quality is assigned but not an importance, it is
  # possible for the importance field to be null. Set it to
  # $NotAClass in this case.
  count = logic_rating.update_null_importance_for_project(wp10db, project)
  logger.info('Updated %s ratings, importance == NotAClass for project: %s',
              count, project.p_project.decode('utf-8'))


def update_project_record(wp10db, project, metadata):
  project_display = project.p_project.decode('utf-8')
  logger.info('Updating project record: %r', project_display)

  num_ratings = logic_rating.count_for_project(wp10db, project)

  n_quality = logic_rating.count_unassessed_quality_for_project(wp10db, project)
  quality_count = num_ratings - n_quality

  n_importance = logic_rating.count_unassessed_importance_for_project(
      wp10db, project)
  importance_count = num_ratings - n_importance

  # Okay, update the fields of the project, warning if we're setting NULLs.
  project.p_timestamp = GLOBAL_TIMESTAMP
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
  project.p_count = num_ratings
  project.p_qcount = quality_count
  project.p_icount = importance_count
  project.p_scope = 0
  project.upload_timestamp = b'00000000000000'

  insert_or_update(wp10db, project)


def update_project(wikidb, wp10db, project, redis=None, track_progress=False):
  extra_assessments = api_project.get_extra_assessments(project.p_project)

  update_project_assessments(wikidb,
                             wp10db,
                             project,
                             extra_assessments,
                             redis=redis,
                             track_progress=track_progress)

  cleanup_project(wp10db, project)

  update_project_record(wp10db, project, extra_assessments)

  ## This is where the old code would update the project scores. However, since
  ## we don't have reliable selection_data at the moment, and we're not sure if
  ## the score metrics will be changing, skip it for now.
  # update_project_scores(wp10_session, project)

  # This is commented out because it can't be done in parallel with other
  # project updates. See https://github.com/openzim/wikimedia_wp1_bot/issues/71
  # update_global_articles_table(wp10db, project)
