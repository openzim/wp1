import attr
import flask
from flask import jsonify, session
from mwoauth import ConsumerToken, Handshaker

from wp1.credentials import CREDENTIALS, ENV
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


@oauth.route("/initiate")
def initiate():
    session["next_path"] = flask.request.args.get("next")
    if session.get("user"):
        homepage_url = get_homepage_url()
        if session.get("next_path"):
            return flask.redirect(f"{homepage_url}{str(session['next_path'])}")
        return flask.redirect(homepage_url)

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

    session["user"] = {
        "access_token": access_token,
        "identity": {"username": identity["username"], "sub": identity["sub"]},
    }

    with wp10db.cursor() as cursor:
        cursor.execute(
            """
      INSERT INTO users (u_id, u_username, u_email)
      VALUES (%(u_id)s, %(u_username)s, %(u_email)s)
      ON DUPLICATE KEY UPDATE
        u_username = VALUES(u_username),
        u_email = VALUES(u_email)
      """,
            {
                "u_id": identity["sub"],
                "u_username": identity["username"],
                "u_email": identity.get("email", None),
            },
        )
        wp10db.commit()
    next_path = session.pop("next_path")
    homepage_url = get_homepage_url()
    if next_path:
        return flask.redirect(f"{homepage_url}{str(next_path)}")
    return flask.redirect(homepage_url)


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
