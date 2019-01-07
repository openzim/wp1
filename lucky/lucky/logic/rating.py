from lucky.constants import GLOBAL_TIMESTAMP, AssessmentKind
from lucky.logic import log as logic_log
from lucky.models.wp10.log import Log
from lucky.models.wp10.rating import Rating

def get_project_ratings(wp10db, project_name):
  # yield from wp10_session.query(Rating).filter(Rating.project == project_name)
  raise NotImplementedError('Need to convert to db access')

def insert(wp10db, rating):
  raise NotImplementedError('Need to convert to db access')

def delete_empty_for_project(wp10db, project):
  raise NotImplementedError('Need to convert to db access')

def update_null_ratings_for_project(wp10db, project, kind):
  raise NotImplementedError('Need to convert to db access')

def count_for_project(wp10db, project):
  # wp10_session.query(Rating).filter(
  #   Rating.project == project.project).count()
  raise NotImplementedError('Need to convert to db access')

def count_unassessed_for_project(wp10db, project, kind):
  # wp10_session.query(Rating).filter(
  #   or_(Rating.quality == not_a_class_db,
  #       Rating.quality == unassessed_db)).filter(
  #       Rating.project == project.project).count()
  raise NotImplementedError('Need to convert to db access')

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

  log = Log(
    l_project=new_rating.r_project, l_namespace=new_rating.r_namespace,
    l_article=new_rating.r_article, l_timestamp=GLOBAL_TIMESTAMP,
    l_action=action, l_old=old_rating_value, l_new=new,
    l_revision_timestamp=timestamp)
  logic_log.insert_or_update(wp10db, log)
