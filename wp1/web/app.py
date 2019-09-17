import os

import flask
import rq_dashboard
from rq_dashboard.cli import add_basic_auth

import wp1.logic.project as logic_project
from wp1.web.db import get_db, has_db


def get_redis_creds():
  try:
    from wp1.credentials import REDIS_CREDS
    return REDIS_CREDS
  except ImportError:
    print('No REDIS_CREDS found, using defaults.')
    return None


def create_app():
  app = flask.Flask(__name__)

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
    if has_db('wikidb'):
      conn = get_db('wikidb')
      conn.close()
    if has_db('wp10db'):
      conn = get_db('wp10db')
      conn.close()

  @app.route('/')
  def index():
    wp10db = get_db('wp10db')
    count = logic_project.count_projects(wp10db)
    return flask.render_template('index.html.jinja2', count=count)

  return app
