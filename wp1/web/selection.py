import flask
from wp1.selection.models.simple_builder import SimpleBuilder
from wp1.web import authenticate
from wp1.wp10_db import connect as wp10_connect

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
  wp10db = wp10_connect()
  simple_builder.insert_builder(data, wp10db)
  if invalid_names:
    return {
        "success": False,
        "items": {
            'valid': valid_names,
            'invalid': invalid_names,
            "errors": errors
        }
    }
  return {"success": True, "items": {}}


@selection.route('/simple/lists')
@authenticate
def get_list_data():
  list_data = []
  simple_builder = SimpleBuilder()
  wp10db = wp10_connect()
  article_lists = simple_builder.get_lists(wp10db)
  for article_data in article_lists['article_lists']:
    list_data.append({
        'list_name': article_data['b_name'].decode('utf-8'),
        'project_name': article_data['b_project'].decode('utf-8'),
        'created_at': article_data['b_created_at'].decode('utf-8')
    })
  return {'list_data': list_data}
