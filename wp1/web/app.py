import os

import flask
import rq_dashboard
from rq_dashboard.cli import add_basic_auth

import wp1.logic.project as logic_project
from wp1.wp10_db import connect as wp10_connect
from wp1.wiki_db import connect as wiki_connect

app = flask.Flask(__name__)

rq_user = os.environ.get('RQ_USER')
rq_pass = os.environ.get('RQ_PASS')

if rq_user is not None and rq_pass is not None:
  app.config.from_object(rq_dashboard.default_settings)
  app.config.update({'RQ_DASHBOARD_REDISH_HOST': 'redis'})
  add_basic_auth(rq_dashboard.blueprint, 'foo', 'bar')
  app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")
else:
  print('No RQ_USER/RQ_PASS found in env, no rq dashboard created')


def has_wp10db():
  return hasattr(flask.g, 'wp10db')


def get_wp10db():
  if not has_wp10db():
    flask.g.wp10db = wp10_connect()
  return flask.g.wp10db


@app.teardown_request
def close_wp10db(ex):
  if has_wp10db():
    conn = get_wp10db()
    conn.close()


def has_wikidb():
  return hasattr(flask.g, 'wikidb')


def get_wikidb():
  if not has_wikidb():
    flask.g.wikidb = wiki_connect()
  return flask.g.wikidb


@app.teardown_request
def close_wikidb(ex):
  if has_wikidb():
    conn = get_wikidb()
    conn.close()


@app.route('/')
def index():
  wp10db = get_wp10db()
  count = logic_project.count_projects(wp10db)
  return flask.render_template('index.html.jinja2', count=count)
