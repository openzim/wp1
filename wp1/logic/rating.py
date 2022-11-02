import logging

import attr

from wp1.conf import get_conf
from wp1.constants import GLOBAL_TIMESTAMP, AssessmentKind
from wp1.logic import log as logic_log
from wp1.models.wp10.log import Log
from wp1.models.wp10.rating import Rating

config = get_conf()
NOT_A_CLASS = config['NOT_A_CLASS']
UNASSESSED_CLASS = config['UNASSESSED_CLASS']

logger = logging.getLogger(__name__)


def get_project_ratings(wp10db, project_name):
  with wp10db.cursor() as cursor:
    cursor.execute(
        'SELECT * FROM ' + Rating.table_name + '''
      WHERE r_project = %(r_project)s
    ''', {'r_project': project_name})
    return [Rating(**db_rating) for db_rating in cursor.fetchall()]


def _project_rating_query(project_name,
                          quality=None,
                          importance=None,
                          project_b_name=None,
                          quality_b=None,
                          importance_b=None,
                          pattern=None,
                          page=None,
                          count=False,
                          limit=100):
  if count:

    query = 'SELECT COUNT(*) as count FROM ' + Rating.table_name + ' as rating_a'
  else:
    if project_b_name is None:
      query = ('SELECT r_project, r_namespace, r_article,'
               ' r_score, r_quality, r_quality_timestamp,'
               ' r_importance, r_importance_timestamp'
               ' FROM ' + Rating.table_name + ' as rating_a')
    else:
      query = (
          'SELECT rating_a.r_project, rating_a.r_namespace, rating_a.r_article,'
          ' rating_a.r_score, rating_a.r_quality, rating_a.r_quality_timestamp,'
          ' rating_a.r_importance, rating_a.r_importance_timestamp, '
          ' rating_b.r_project, rating_b.r_article, rating_b.r_namespace,'
          ' rating_b.r_quality, rating_b.r_importance'
          ' FROM ' + Rating.table_name + ' as rating_a')

  if project_b_name is not None:
    query += (' JOIN ' + Rating.table_name + ' as rating_b'
              ' ON rating_a.r_article = rating_b.r_article'
              ' AND rating_a.r_namespace = rating_b.r_namespace')

  if project_b_name is None:
    if importance is None:
      query += (' LEFT JOIN global_rankings gri ON gri.gr_rating = r_importance'
                '   AND gri.gr_type = "importance"')
    if quality is None:
      query += (
          ' LEFT JOIN global_rankings grq ON grq.gr_rating = rating_a.r_quality'
          '   AND grq.gr_type = "quality" ')

  query += ' WHERE rating_a.r_project = %(r_project)s'
  if project_b_name is not None:
    query += ' AND rating_b.r_project = %(r_project_b)s'

  if pattern is not None:
    query += ' AND rating_a.r_article LIKE %(article_pattern_compiled)s'

  if quality is not None:
    if quality == b'Assessed-Class':
      query += ' AND rating_a.r_quality != "Unassessed-Class"'
    else:
      query += ' AND rating_a.r_quality = %(r_quality)s'
  if importance is not None:
    query += ' AND rating_a.r_importance = %(r_importance)s'

  if project_b_name is not None:
    if quality_b is not None:
      if quality_b == b'Assessed-Class':
        query += ' AND rating_b.r_quality != "Unassessed-Class"'
      else:
        query += ' AND rating_b.r_quality = %(r_quality_b)s'
    if importance_b is not None:
      query += ' AND rating_b.r_importance = %(r_importance_b)s'

  if project_b_name is None:
    if quality is None and importance is None:
      query += ' ORDER BY grq.gr_ranking DESC, gri.gr_ranking DESC, rating_a.r_article'
    elif quality is None:
      query += ' ORDER BY grq.gr_ranking DESC, rating_a.r_article'
    elif importance is None:
      query += ' ORDER BY gri.gr_ranking DESC, rating_a.r_article'

  if page is not None:
    page = int(page) - 1
    query += ' LIMIT %s,%s' % (page * limit, limit)
  else:
    query += ' LIMIT %s' % limit

  logger.debug(query)
  return query


def get_project_rating_count_by_type(wp10db,
                                     project_name,
                                     quality=None,
                                     importance=None,
                                     project_b_name=None,
                                     quality_b=None,
                                     importance_b=None,
                                     pattern=None):
  query = _project_rating_query(project_name,
                                quality=quality,
                                importance=importance,
                                project_b_name=project_b_name,
                                quality_b=quality_b,
                                importance_b=importance_b,
                                pattern=pattern,
                                count=True)

  params = {
      'r_project': project_name,
      'r_quality': quality,
      'r_importance': importance,
  }

  if pattern is not None:
    params['article_pattern_compiled'] = '%' + pattern + '%'
  if project_b_name is not None:
    params['r_project_b'] = project_b_name
  if quality_b is not None:
    params['r_quality_b'] = quality_b
  if importance_b is not None:
    params['r_importance_b'] = importance_b

  with wp10db.cursor() as cursor:
    cursor.execute(query, params)
    res = cursor.fetchone()
    return res['count']


def get_project_rating_by_type(wp10db,
                               project_name,
                               quality=None,
                               importance=None,
                               project_b_name=None,
                               quality_b=None,
                               importance_b=None,
                               pattern=None,
                               page=None,
                               limit=100):
  try:
    limit = int(limit)
  except ValueError:
    limit = 100
  if limit < 0:
    limit = 100
  if limit > 500:
    limit = 500

  query = _project_rating_query(project_name,
                                quality=quality,
                                importance=importance,
                                project_b_name=project_b_name,
                                quality_b=quality_b,
                                importance_b=importance_b,
                                pattern=pattern,
                                page=page,
                                limit=limit)
  params = {
      'r_project': project_name,
      'r_quality': quality,
      'r_importance': importance,
  }

  if pattern is not None:
    params['article_pattern_compiled'] = '%' + pattern + '%'
  if project_b_name is not None:
    params['r_project_b'] = project_b_name
  if quality_b is not None:
    params['r_quality_b'] = quality_b
  if importance_b is not None:
    params['r_importance_b'] = importance_b

  with wp10db.cursor() as cursor:
    cursor.execute(query, params)
    if project_b_name is None:
      return [Rating(**db_rating) for db_rating in cursor.fetchall()]

    results = []
    for res in cursor.fetchall():
      rating_b = Rating(r_project=res.pop('rating_b.r_project'),
                        r_article=res.pop('rating_b.r_article'),
                        r_namespace=res.pop('rating_b.r_namespace'),
                        r_quality=res.pop('rating_b.r_quality'),
                        r_importance=res.pop('rating_b.r_importance'))
      rating_a = Rating(**res)
      results.append((rating_a, rating_b))
    return results


def get_all_ratings_count_for_project(wp10db, project_name):
  with wp10db.cursor() as cursor:
    cursor.execute('SELECT COUNT(*) as count FROM ratings WHERE r_project = %s',
                   (project_name,))

    res = cursor.fetchone()
    return res['count']


def insert_or_update(wp10db, rating, kind):
  duplicate_clause = ''
  if kind == AssessmentKind.QUALITY:
    duplicate_clause = '''
      ON DUPLICATE KEY UPDATE r_quality=%(r_quality)s,
                              r_quality_timestamp=%(r_quality_timestamp)s
    '''
  elif kind == AssessmentKind.IMPORTANCE:
    duplicate_clause = '''
      ON DUPLICATE KEY UPDATE r_importance=%(r_importance)s,
                              r_importance_timestamp=%(r_importance_timestamp)s
    '''
  elif kind == AssessmentKind.BOTH:
    duplicate_clause = '''
      ON DUPLICATE KEY UPDATE r_quality=%(r_quality)s,
                              r_quality_timestamp=%(r_quality_timestamp)s,
                              r_importance=%(r_importance)s,
                              r_importance_timestamp=%(r_importance_timestamp)s
    '''
  else:
    raise ValueError('AssessmentKind was not QUALITY or IMPORTANCE: %s', kind)

  with wp10db.cursor() as cursor:
    cursor.execute(
        '''
        INSERT INTO ratings
          (r_project, r_namespace, r_article, r_score, r_quality,
           r_quality_timestamp, r_importance, r_importance_timestamp)
        VALUES
          (%(r_project)s, %(r_namespace)s, %(r_article)s, %(r_score)s,
           %(r_quality)s, %(r_quality_timestamp)s, %(r_importance)s,
           %(r_importance_timestamp)s)
    ''' + duplicate_clause, attr.asdict(rating))


def delete_empty_for_project(wp10db, project):
  not_a_class_db = NOT_A_CLASS.encode('utf-8')
  with wp10db.cursor() as cursor:
    args = {'r_project': project.p_project, 'not_a_class': not_a_class_db}
    cursor.execute(
        '''
        DELETE FROM ratings
        WHERE r_project=%(r_project)s AND
              (r_quality IS NULL OR r_quality=%(not_a_class)s) AND
              (r_importance IS NULL OR r_importance=%(not_a_class)s)
    ''', args)
    return cursor.rowcount


def update_null_quality_for_project(wp10db, project):
  not_a_class_db = NOT_A_CLASS.encode('utf-8')
  with wp10db.cursor() as cursor:
    args = {'r_project': project.p_project, 'not_a_class': not_a_class_db}
    cursor.execute(
        '''
        UPDATE ratings
          SET r_quality = %(not_a_class)s,
              r_quality_timestamp=r_importance_timestamp
        WHERE r_project=%(r_project)s AND
              r_quality IS NULL
    ''', args)
    return cursor.rowcount


def update_null_importance_for_project(wp10db, project):
  not_a_class_db = NOT_A_CLASS.encode('utf-8')
  with wp10db.cursor() as cursor:
    args = {'r_project': project.p_project, 'not_a_class': not_a_class_db}
    cursor.execute(
        '''
        UPDATE ratings
          SET r_importance = %(not_a_class)s,
              r_importance_timestamp=r_quality_timestamp
        WHERE r_project=%(r_project)s AND
              r_importance IS NULL
    ''', args)
    return cursor.rowcount


def count_for_project(wp10db, project):
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''
        SELECT COUNT(*) as cnt FROM ratings
        WHERE r_project=%(r_project)s
    ''', {'r_project': project.p_project})
    return cursor.fetchone()['cnt']


def count_unassessed_quality_for_project(wp10db, project):
  not_a_class_db = NOT_A_CLASS.encode('utf-8')
  unassessed_db = UNASSESSED_CLASS.encode('utf-8')
  with wp10db.cursor() as cursor:
    args = {
        'r_project': project.p_project,
        'not_a_class': not_a_class_db,
        'unassessed': unassessed_db
    }
    cursor.execute(
        '''
        SELECT COUNT(*) as cnt FROM ratings
        WHERE (r_quality = %(not_a_class)s OR r_quality = %(unassessed)s) AND
              r_project = %(r_project)s
    ''', args)
    return cursor.fetchone()['cnt']


def count_unassessed_importance_for_project(wp10db, project):
  not_a_class_db = NOT_A_CLASS.encode('utf-8')
  unassessed_db = UNASSESSED_CLASS.encode('utf-8')
  with wp10db.cursor() as cursor:
    args = {
        'r_project': project.p_project,
        'not_a_class': not_a_class_db,
        'unassessed': unassessed_db
    }
    cursor.execute(
        '''
        SELECT COUNT(*) as cnt FROM ratings
        WHERE (r_importance = %(not_a_class)s OR
               r_importance = %(unassessed)s) AND
              r_project = %(r_project)s
    ''', args)
    return cursor.fetchone()['cnt']


def add_log_for_rating(wp10db, new_rating, kind, old_rating_value):
  if kind == AssessmentKind.QUALITY:
    action = b'quality'
    timestamp = new_rating.r_quality_timestamp
    new = new_rating.r_quality
  elif kind == AssessmentKind.IMPORTANCE:
    action = b'importance'
    timestamp = new_rating.r_importance_timestamp
    new = new_rating.r_importance
  else:
    raise ValueError('Unrecognized value for kind: %s', kind)

  log = Log(l_project=new_rating.r_project,
            l_namespace=new_rating.r_namespace,
            l_article=new_rating.r_article,
            l_timestamp=GLOBAL_TIMESTAMP,
            l_action=action,
            l_old=old_rating_value,
            l_new=new,
            l_revision_timestamp=timestamp)
  logic_log.insert_or_update(wp10db, log)
