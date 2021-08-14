import flask
from flask import session

from wp1.constants import CONTENT_TYPE_TO_EXT
from wp1.logic.builder import get_lists, save_builder
from wp1.selection.models.simple_builder import SimpleBuilder
from wp1.web import authenticate
from wp1.web.db import get_db

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


@selection.route('/simple/lists')
@authenticate
def get_list_data():
  result = {}
  wp10db = get_db('wp10db')
  user_id = session['user']['identity']['sub']
  article_lists = get_lists(wp10db, user_id)
  for data in article_lists:
    if not data['b_id'] in result:
      result[data['b_id']] = {
          'name': data['b_name'].decode('utf-8'),
          'project': data['b_project'].decode('utf-8'),
          'selections_data': []
      }
    result[data['b_id']]['selections_data'].append({
        'content_type': data['s_content_type'].decode('utf-8'),
        'selection_url': 'https://www.example.com/<id>'
    })
  return {'list_data': result}
