import flask
from functools import wraps
from flask import session


def authenticate(f):

  @wraps(f)
  def wrapper(*args, **kwargs):
    if session.get('user'):
      return f(*args, **kwargs)
    flask.abort(401, 'Unauthorized')

  return wrapper
