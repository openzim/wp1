from datetime import datetime
from functools import wraps, update_wrapper
from flask_session import Session
import os
import flask
import flask_cors
import flask_gzip
import redis
import rq_dashboard
from rq_dashboard.cli import add_basic_auth

import wp1.logic.project as logic_project
from wp1 import environment
from wp1.web.db import get_db, has_db
from wp1.web.articles import articles
from wp1.web.projects import projects
from wp1.web.selection import selection
from wp1.web.sites import sites
from wp1.web.dev.projects import dev_projects

try:
  # The credentials module isn't checked in and may be missing
  from wp1.credentials import ENV, CREDENTIALS
except ImportError:
  print('No credentials.py file found. Development overlay will '
        'not be enabled.')
  ENV = None
  CREDENTIALS = None


def get_redis_creds():
  try:
    from wp1.credentials import ENV, CREDENTIALS
    return CREDENTIALS[ENV]['REDIS']
  except ImportError:
    print('No REDIS_CREDS found, using defaults.')
    return None


def get_secret_key():
  try:
    from wp1.credentials import ENV, CREDENTIALS
    return CREDENTIALS[ENV]['SESSION']['secret_key']
  except ImportError:
    print('No secret_key found, using defaults.')
    return 'WP1'


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
  missing_credentials = CREDENTIALS is None or ENV is None

  cors_origins = None
  if not missing_credentials:
    cors_origins = CREDENTIALS[ENV].get('CLIENT_URL', {}).get('domains')
  if cors_origins is None:
    cors_origins = '*'

  cors = flask_cors.CORS(app,
                         resources='*',
                         origins=cors_origins,
                         supports_credentials=True)
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

  if redis_creds is not None:
    app.config['SESSION_REDIS'] = redis.from_url('redis://{}:{}'.format(
        redis_creds['host'], redis_creds['port']))

  app.config['SECRET_KEY'] = get_secret_key()
  app.config['SESSION_TYPE'] = 'redis'
  Session(app)

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

  if ENV == environment.Environment.DEVELOPMENT:
    # In development, override some project endpoints, mostly manual
    # update, to provide an easier env for developing the frontend.
    print('DEVELOPMENT: overlaying dev_projects blueprint. '
          'Some endpoints will be replaced with development versions')
    app.register_blueprint(dev_projects, url_prefix='/v1/projects')

  app.register_blueprint(projects, url_prefix='/v1/projects')
  app.register_blueprint(articles, url_prefix='/v1/articles')
  app.register_blueprint(sites, url_prefix='/v1/sites')
  app.register_blueprint(selection, url_prefix='/v1/selection')

  if not missing_credentials:
    mwoauth = CREDENTIALS.get(ENV, {}).get('MWOAUTH', {})
  if not (missing_credentials or mwoauth.get('consumer_key') is None or
          mwoauth.get('consumer_secret') is None):
    from wp1.web.oauth import oauth
    app.register_blueprint(oauth, url_prefix='/v1/oauth')

  return app
