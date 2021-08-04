from wp1.selection.models.simple_builder import SimpleBuilder
import flask
from wp1.web import authenticate

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
  valid_names, invalid_names, forbiden_chars = simple_builder.validate(**params)
  if invalid_names:
    return {
        "success": False,
        "items": {
            'valid': valid_names,
            'invalid': invalid_names,
            "forbiden_chars": forbiden_chars
        }
    }
  return {"success": True, "items": {}}
