import flask
from wp1.web import authenticate
import wp1.logic.selection as selections

selection = flask.Blueprint('selection', __name__)


@selection.route('/simple', methods=['POST'])
def create():
  data = flask.request.get_json()
  list_name = data['list_name']
  articles = data['articles']
  project = data['project']
  if not articles or not list_name or not project:
    flask.abort(400)
  valid_names, invalid_names, forbiden_chars = selections.validate_list(
      articles)
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
