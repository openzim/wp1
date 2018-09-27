from models.wp10.rating import Rating

def get_project_ratings(wp10_session, project_name):
  yield from wp10_session.query(Rating).filter(Rating.project == project_name)
