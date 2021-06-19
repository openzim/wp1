import attr
import flask
from flask import jsonify, session
from mwoauth import ConsumerToken, Handshaker
from wp1.web.db import get_db
from wp1.models.wp10.user import User

oauth = flask.Blueprint('oauth', __name__)

try:
  # The credentials module isn't checked in and may be missing
  from wp1.credentials import ENV, CREDENTIALS
  consumer_token = ConsumerToken(CREDENTIALS[ENV]['MWOAUTH']['consumer_key'],
                                 CREDENTIALS[ENV]['MWOAUTH']['consumer_secret'])
  handshaker = Handshaker("https://en.wikipedia.org/w/index.php",
                          consumer_token)
  homepage_url = CREDENTIALS[ENV]['CLIENT_URL']['homepage']
except ImportError:
  print('No credentials.py file found, Please add your '
        'mwoauth credentials in credentials.py')
  ENV = None
  CREDENTIALS = None
  handshaker = None
  homepage_url = None


@oauth.route('/initiate')
def initiate():
  session['next_path'] = flask.request.args.get('next')
  if session.get('user'):
    if session.get('next_path'):
      return flask.redirect(f"{homepage_url}{str(session['next_path'])}")
    return flask.redirect(homepage_url)
  redirect, request_token = handshaker.initiate()
  session['request_token'] = request_token
  return flask.redirect(redirect)


@oauth.route('/complete')
def complete():
  if 'request_token' not in session:
    flask.abort(404, 'User does not exist')

  query_string = str(flask.request.query_string.decode('utf-8'))
  access_token = handshaker.complete(session['request_token'], query_string)
  session.pop('request_token')
  identity = handshaker.identify(access_token)

  session['user'] = {
      'access_token': access_token,
      'identity': {
          'username': identity['username'],
          'sub': identity['sub']
      }
  }
  wp10db = get_db('wp10db')
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''INSERT INTO users (u_id, u_username)
                      VALUES (%(u_id)s, %(u_username)s)
                      ON DUPLICATE KEY UPDATE u_id= %(u_id)s, u_username= %(u_username)s''',
        {
            'u_id': identity['sub'],
            'u_username': identity['username']
        })
    wp10db.commit()
  next_path = session.pop('next_path')
  if next_path:
    return flask.redirect(f"{homepage_url}{str(next_path)}")
  return flask.redirect(homepage_url)


@oauth.route('/identify')
def identify():
  user = session.get('user')
  if user is None:
    flask.abort(401, 'Unauthorized')
  return jsonify({'username': user['identity']['username']})


@oauth.route('/logout')
def logout():
  if session.get('user') is None:
    flask.abort(404, 'User does not exist')
  session.pop('user')
  return {'status': '204'}
