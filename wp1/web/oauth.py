import flask
from flask import jsonify, session
from mwoauth import ConsumerToken, Handshaker
from oauthlib.oauth1.rfc5849 import Client

oauth = flask.Blueprint('oauth', __name__)

try:
  # The credentials module isn't checked in and may be missing
  from wp1.credentials import ENV, CREDENTIALS
  consumer_token = ConsumerToken(CREDENTIALS[ENV]['MWOAUTH']['consumer_key'],
                                 CREDENTIALS[ENV]['MWOAUTH']['consumer_secret'])
  handshaker = Handshaker("https://en.wikipedia.org/w/index.php",
                          consumer_token)
  client_url = CREDENTIALS[ENV]['CLIENT_URL']
except ImportError:
  print(
      'No credentials.py file found, Please add your mwoauth credentials in credentials.py'
  )


@oauth.route('/initiate')
def initiate():
  if session.get('user'):
    return flask.redirect(client_url)
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
  session['user'] = {'access_token': access_token, 'identity': identity}
  return flask.redirect(client_url)


@oauth.route('/identify')
def identify():
  user = session.get('user')
  if user is None:
    flask.abort(401, 'Unauthorized')
    return
  return jsonify({'username': user['identity']['username']})


@oauth.route('/logout')
def logout():
  if session.get('user') is None:
    flask.abort(404, 'User does not exist')
  session.pop('user')
  return {'status': '204'}
