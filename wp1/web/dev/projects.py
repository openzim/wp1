import flask

projects = flask.Blueprint('dev_projects', __name__)


@projects.route('/count')
def count():
  return flask.jsonify({'count': 42})
