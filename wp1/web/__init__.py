import flask
from functools import wraps
from flask import session

try:
  #  The credentials module isn't checked in and may be missing
  from wp1.credentials import ENV, CREDENTIALS
except ImportError:
  print(
      'No credentials.py file found, Please add your credentials in credentials.py'
  )
  ENV = None
  CREDENTIALS = None


def authenticate(f):

  @wraps(f)
  def wrapper(*args, **kwargs):
    if session.get('user'):
      return f(*args, **kwargs)
    flask.abort(401, 'Unauthorized')

  return wrapper
