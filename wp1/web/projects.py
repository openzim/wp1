import attr
import flask

from wp1.web.db import get_db
import wp1.logic.project as logic_project
import wp1.tables as tables

projects = flask.Blueprint('projects', __name__)


@projects.route('/')
def list_():
  wp10db = get_db('wp10db')
  projects = logic_project.list_all_projects(wp10db)
  return flask.jsonify(list(project.to_web_dict() for project in projects))


@projects.route('/count')
def count():
  wp10db = get_db('wp10db')
  count = logic_project.count_projects(wp10db)
  return flask.jsonify({'count': count})


@projects.route('/<project_name>/table')
def table(project_name):
  wp10db = get_db('wp10db')
  project_name_bytes = project_name.encode('utf-8')
  data = tables.generate_project_table_data(wp10db, project_name_bytes)
  data = tables.convert_table_data_for_web(data)

  return flask.jsonify({'table_data': data})
