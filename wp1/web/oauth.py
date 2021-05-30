import flask
import jwt
from flask import request, jsonify, session
from mwoauth import ConsumerToken, Handshaker, RequestToken
from wp1.credentials import ENV, CREDENTIALS

oauth = flask.Blueprint('oauth', __name__)

consumer_token = ConsumerToken(CREDENTIALS[ENV]['MWOAUTH']['consumer_key'],
                               CREDENTIALS[ENV]['MWOAUTH']['consumer_secret'])

handshaker = Handshaker("https://en.wikipedia.org/w/index.php", consumer_token)


@oauth.route('/initiate')
def initiate():
  redirect, request_token = handshaker.initiate()
  session[str(request_token.key)] = dict(
      zip(request_token._fields, request_token))
  return flask.redirect(redirect)


@oauth.route('/complete')
def complete():
  request_token_key = str(flask.request.args.get('oauth_token', 'None'))
  query_string = str(flask.request.query_string.decode('utf-8'))
  access_token = handshaker.complete(RequestToken(**session[request_token_key]),
                                     query_string)
  session.pop(request_token_key)
  session[request_token_key] = dict(zip(access_token._fields, access_token))
  return flask.redirect('{}?{}'.format(CREDENTIALS[ENV]['CLIENT_URL'],
                                       request_token_key))


@oauth.route('/token')
def token():
  request_token = request.get_json(force=True)
  access_token = session[request_token]
  encoded_jwt = jwt.encode({"access": access_token},
                           CREDENTIALS[ENV]['SESSION']['secret_key'],
                           algorithm="HS256")
  return jsonify(encoded_jwt)


# @oauth.route('/identify')


@oauth.route('/logout', methods=['POST'])
def logout():
  request_token = request.get_json(force=True)
  session.pop(request_token)
  return {'status': '200'}
