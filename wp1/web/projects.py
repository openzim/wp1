import attr
import flask

from wp1.web.db import get_db
import wp1.logic.project as logic_project

projects = flask.Blueprint('projects', __name__)


@projects.route('/')
def list_():
  wp10db = get_db('wp10db')
  projects = logic_project.list(wp10db)
  return flask.jsonify(list(project.to_web_dict() for project in projects))


@projects.route('/count')
def count():
  wp10db = get_db('wp10db')
  count = logic_project.count_projects(wp10db)
  return flask.jsonify({'count': count})
