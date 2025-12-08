    import attr
import flask
from flask import jsonify, session
from mwoauth import ConsumerToken, Handshaker

from wp1 import environment
from wp1.credentials import CREDENTIALS, ENV
from wp1.logic import users as logic_users
from wp1.models.wp10.user import User
from wp1.web.db import get_db

oauth = flask.Blueprint("oauth", __name__)


def get_handshaker():
    consumer_token = ConsumerToken(
        CREDENTIALS[ENV]["MWOAUTH"]["consumer_key"],
        CREDENTIALS[ENV]["MWOAUTH"]["consumer_secret"],
    )
    handshaker = Handshaker("https://en.wikipedia.org/w/index.php", consumer_token)
    return handshaker


def get_homepage_url():
    return CREDENTIALS[ENV]["CLIENT_URL"]["homepage"]


def has_oauth_credentials():
  try:
    oauth_creds = CREDENTIALS[ENV].get('MWOAUTH', {})
    consumer_key = oauth_creds.get('consumer_key', '')
    consumer_secret = oauth_creds.get('consumer_secret', '')
    return bool(consumer_key and consumer_secret)
  except (KeyError, AttributeError):
    return False


def create_fake_dev_user():
  fake_identity = {
      'username': 'dev_user',
      'sub': 'dev_user_12345',
      'email': 'dev_user@example.com'
  }
  fake_access_token = {
      'key': 'dev_access_token',
      'secret': 'dev_access_secret'
  }
  return fake_identity, fake_access_token


def create_user_session(identity, access_token):
  return {
      'access_token': access_token,
      'identity': {
          'username': identity['username'],
          'sub': identity['sub']
      }
  }


def redirect_after_login():
  next_path = session.pop('next_path', None)
  homepage_url = get_homepage_url()
  if next_path:
    return flask.redirect(f"{homepage_url}{str(next_path)}")
  return flask.redirect(homepage_url)


@oauth.route('/initiate')
def initiate():
  session['next_path'] = flask.request.args.get('next')
  if session.get('user'):
    return redirect_after_login()

  # In development mode, use fake user if OAuth credentials are not configured
  if (ENV == environment.Environment.DEVELOPMENT and
      not has_oauth_credentials()):
    fake_identity, fake_access_token = create_fake_dev_user()
    wp10db = get_db('wp10db')

    # Only create user if it doesn't already exisst
    if not logic_users.user_exists(wp10db, fake_identity['sub']):
      logic_users.create_or_update_user(wp10db, fake_identity['sub'],
                                       fake_identity['username'],
                                       fake_identity.get('email', None))

    session['user'] = create_user_session(fake_identity, fake_access_token)
    return redirect_after_login()

  handshaker = get_handshaker()
  redirect, request_token = handshaker.initiate()
  session["request_token"] = request_token
  return flask.redirect(redirect)


@oauth.route("/complete")
def complete():
    if "request_token" not in session:
        flask.abort(404, "User does not exist")

    handshaker = get_handshaker()
    query_string = str(flask.request.query_string.decode("utf-8"))
    access_token = handshaker.complete(session["request_token"], query_string)
    session.pop("request_token")
    identity = handshaker.identify(access_token)

    wp10db = get_db("wp10db")

    logic_users.create_or_update_user(wp10db, identity['sub'],
                                   identity['username'],
                                   identity.get('email', None))

    session['user'] = create_user_session(identity, access_token)
    return redirect_after_login()


@oauth.route("/identify")
def identify():
    user = session.get("user")
    if user is None:
        flask.abort(401, "Unauthorized")
    return jsonify({"username": user["identity"]["username"]})


@oauth.route("/email")
def email():
    user = session.get("user")
    if user is None:
        flask.abort(401, "Unauthorized")
    email = user["identity"].get("email")
    if email is None:
        wp10db = get_db("wp10db")
        with wp10db.cursor() as cursor:
            cursor.execute(
                "SELECT u_email FROM users WHERE u_id = %s", (user["identity"]["sub"],)
            )
            result = cursor.fetchone()
            if result:
                raw_email = result["u_email"]
                if raw_email is not None:
                    email = raw_email.decode("utf-8")
            user["identity"]["email"] = email
            session["user"] = user
    return jsonify({"email": email})


@oauth.route("/logout")
def logout():
    if session.get("user") is None:
        flask.abort(404, "User does not exist")
    session.pop("user")
    return {"status": "204"}
