from lucky.constants import GLOBAL_TIMESTAMP, AssessmentKind
from lucky.models.wp10.log import Log
from lucky.models.wp10.rating import Rating

def get_project_ratings(wp10_session, project_name):
  yield from wp10_session.query(Rating).filter(Rating.project == project_name)

def add_log_for_rating(wp10_session, new_rating, kind, old_rating_value):
  if kind == AssessmentKind.QUALITY:
    action = b'quality'
    timestamp = new_rating.quality_timestamp
    new = new_rating.quality
  elif kind == AssessmentKind.IMPORTANCE:
    action = b'importance'
    timestamp = new_rating.importance_timestamp
    new = new_rating.importance
  else:
    raise ValueError('Unrecognized value for kind: %s', kind)

  log = Log(
    project=new_rating.project, namespace=new_rating.namespace,
    article=new_rating.article, timestamp=GLOBAL_TIMESTAMP, action=action,
    old=old_rating_value, new=new, revision_timestamp=timestamp)
  log = wp10_session.merge(log)
  wp10_session.add(log)
