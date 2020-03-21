from datetime import datetime
from functools import wraps, update_wrapper
import os

import flask
import flask_cors
import flask_gzip
import rq_dashboard
from rq_dashboard.cli import add_basic_auth

import wp1.logic.project as logic_project
from wp1.web.db import get_db, has_db
from wp1.web.projects import projects


def get_redis_creds():
  try:
    from wp1.credentials import REDIS_CREDS
    return REDIS_CREDS
  except ImportError:
    print('No REDIS_CREDS found, using defaults.')
    return None


SWAGGER_UI_DIST_DIR = "swagger-ui-dist"


# We use this to prevent caching of `/swagger.yml`
# Credits: https://arusahni.net/blog/2014/03/flask-nocache.html
def nocache(view):

  @wraps(view)
  def no_cache(*args, **kwargs):
    response = flask.make_response(view(*args, **kwargs))
    response.headers["Last-Modified"] = datetime.now()
    response.headers[
        "Cache-Control"] = "no-store, no-cache, must-revalidate, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "-1"
    return response

  return update_wrapper(no_cache, view)


def create_app():
  app = flask.Flask(__name__)
  cors = flask_cors.CORS(app)
  gzip = flask_gzip.Gzip(app, minimum_size=256)

  rq_user = os.environ.get('RQ_USER')
  rq_pass = os.environ.get('RQ_PASS')
  redis_creds = get_redis_creds()

  if rq_user is not None and rq_pass is not None:
    app.config.from_object(rq_dashboard.default_settings)
    if redis_creds is not None:
      app.config.update({'RQ_DASHBOARD_REDIS_HOST': redis_creds['host']})
      app.config.update({'RQ_DASHBOARD_REDIS_PORT': redis_creds['port']})
    add_basic_auth(rq_dashboard.blueprint, rq_user, rq_pass)
    app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")
  else:
    print('No RQ_USER/RQ_PASS found in env. RQ dashboard not created.')

  @app.teardown_request
  def close_dbs(ex):
    if has_db('wp10db'):
      conn = get_db('wp10db')
      conn.close()

  @app.route('/')
  def index():
    return flask.send_from_directory('.', "swagger.html")

  @app.route("/v1/openapi.yml")
  @nocache
  def swagger_api_docs_yml():
    return flask.send_from_directory(".", "openapi.yml")

  app.register_blueprint(projects, url_prefix='/v1/projects')

  return app
