import flask
from flask import session
from wp1.web import authenticate
from wp1.web.db import get_db
from wp1.logic.builder import save_builder
from wp1.selection.models.simple_builder import SimpleBuilder

selection = flask.Blueprint('selection', __name__)


@selection.route('/simple', methods=['POST'])
@authenticate
def create():
  data = flask.request.get_json()
  list_name = data['list_name']
  articles = data['articles']
  project = data['project']
  params = {'list': articles.split('\n')}
  if not articles or not list_name or not project:
    flask.abort(400)
  simple_builder = SimpleBuilder()
  valid_names, invalid_names, errors = simple_builder.validate(**params)
  if invalid_names:
    return {
        "success": False,
        "items": {
            'valid': valid_names,
            'invalid': invalid_names,
            "errors": errors
        }
    }
  user_id = session['user']['identity']['sub']
  wp10db = get_db('wp10db')
  save_builder(wp10db, list_name, user_id, project, articles)
  return {"success": True, "items": {}}
