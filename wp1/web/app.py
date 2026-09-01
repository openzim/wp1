import os
from datetime import datetime
from functools import update_wrapper, wraps

import flask
import flask_cors
import flask_gzip
import redis
from flask_session import Session
from werkzeug.exceptions import HTTPException

import wp1.logic.project as logic_project
from wp1 import environment
from wp1.config import get_settings
from wp1.web.articles import articles
from wp1.web.builders import builders
from wp1.web.db import get_db, has_db
from wp1.web.dev.projects import dev_projects
from wp1.web.oauth import oauth
from wp1.web.projects import projects
from wp1.web.selection import selection
from wp1.web.sites import sites
from wp1.web.zim_emails import zim_emails


def get_secret_key():
    return get_settings().SESSION_SECRET_KEY


# We use this to prevent caching of `/swagger.yml`
# Credits: https://arusahni.net/blog/2014/03/flask-nocache.html
def nocache(view):

    @wraps(view)
    def no_cache(*args, **kwargs):
        response = flask.make_response(view(*args, **kwargs))
        response.headers["Last-Modified"] = datetime.now()
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, pre-check=0, max-age=0"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "-1"
        return response

    return update_wrapper(no_cache, view)


def create_app(session_type="redis"):
    app = flask.Flask(__name__)

    settings = get_settings()

    cors_origins = settings.CLIENT_DOMAINS or "*"

    cors = flask_cors.CORS(
        app, resources="*", origins=cors_origins, supports_credentials=True
    )
    gzip = flask_gzip.Gzip(app, minimum_size=256)

    app.config["SESSION_REDIS"] = redis.from_url(
        "redis://{}:{}".format(settings.REDIS_HOST, settings.REDIS_PORT)
    )

    app.config["SECRET_KEY"] = get_secret_key()
    app.config["SESSION_TYPE"] = session_type
    Session(app)

    @app.teardown_request
    def close_dbs(ex):
        if has_db("wp10db"):
            # Pop rather than get: Flask runs teardown a second time when a
            # test client's preserved request context is finally popped, and
            # pymysql raises if the connection is closed twice.
            conn = flask.g.pop("wp10db")
            conn.close()

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        # Return errors as JSON, with the description passed to flask.abort()
        # (or the werkzeug default), instead of the default HTML error page.
        return flask.jsonify({"error": e.description}), e.code

    @app.route("/")
    def index():
        return flask.send_from_directory(".", "swagger.html")

    @app.route("/v1/openapi.yml")
    @nocache
    def swagger_api_docs_yml():
        return flask.send_from_directory(".", "openapi.yml")

    if get_settings().ENV == environment.Environment.DEVELOPMENT:
        # In development, override some project endpoints, mostly manual
        # update, to provide an easier env for developing the frontend.
        print(
            "DEVELOPMENT: overlaying dev_projects blueprint. "
            "Some endpoints will be replaced with development versions"
        )
        app.register_blueprint(dev_projects, url_prefix="/v1/projects")

    app.register_blueprint(projects, url_prefix="/v1/projects")
    app.register_blueprint(articles, url_prefix="/v1/articles")
    app.register_blueprint(sites, url_prefix="/v1/sites")
    app.register_blueprint(selection, url_prefix="/v1/selection")
    app.register_blueprint(builders, url_prefix="/v1/builders")
    app.register_blueprint(zim_emails, url_prefix="/v1/zim")
    app.register_blueprint(oauth, url_prefix="/v1/oauth")

    return app
    return app
    return app
