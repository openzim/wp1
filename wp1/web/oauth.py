import flask
from flask import jsonify, session
from mwoauth import ConsumerToken, Handshaker

oauth = flask.Blueprint('oauth', __name__)

try:
  # The credentials module isn't checked in and may be missing
  from wp1.credentials import ENV, CREDENTIALS
  consumer_token = ConsumerToken(CREDENTIALS[ENV]['MWOAUTH']['consumer_key'],
                                 CREDENTIALS[ENV]['MWOAUTH']['consumer_secret'])
  handshaker = Handshaker("https://en.wikipedia.org/w/index.php",
                          consumer_token)
except ImportError:
  print(
      'No credentials.py file found, Please add your mwoauth credentials in credentials.py'
  )


@oauth.route('/initiate')
def initiate():
  redirect, request_token = handshaker.initiate()
  session['request_token'] = request_token
  return flask.redirect(redirect)


@oauth.route('/complete')
def complete():
  try:
    query_string = str(flask.request.query_string.decode('utf-8'))
    access_token = handshaker.complete(session['request_token'], query_string)
    session.pop('request_token')
    session['access_token'] = access_token
    return {'status:': '200'}
  except KeyError:
    flask.abort(404, 'User does not exist')


@oauth.route('/identify')
def identify():
  try:
    username = handshaker.identify(session['access_token'])['username']
    return jsonify(username)
  except KeyError:
    flask.abort(401, 'Unauthorized')


@oauth.route('/logout')
def logout():
  try:
    session.pop('access_token')
    return {'status': '200'}
  except KeyError:
    flask.abort(404, 'User does not exist')
