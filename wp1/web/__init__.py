import flask
from functools import wraps
from flask import session

from wp1.config import http_origin


def authenticate(f):

    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("user"):
            if flask.request.method not in ("GET", "HEAD", "OPTIONS"):
                origin = flask.request.headers.get("Origin")
                if origin is None:
                    origin = http_origin(
                        flask.request.headers.get("Referer"), referer=True
                    )
                else:
                    origin = http_origin(origin)
                if origin not in flask.current_app.config["TRUSTED_CLIENT_ORIGINS"]:
                    flask.abort(403, "A trusted Origin or Referer is required")
            return f(*args, **kwargs)
        flask.abort(401, "Unauthorized")

    return wrapper
