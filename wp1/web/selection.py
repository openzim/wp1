import flask
from wp1.web import authenticate
import wp1.logic.selection as selections

selection = flask.Blueprint('selection', __name__)


@selection.route('/simple', methods=['POST'])
def create():
  response = flask.request.get_json()
  list_name = response['list_name']
  items = response['article_name']
  project = response['project_name']
  if not items or not list_name or not project:
    flask.abort(400)
  valid_article_names, invalid_article_names, forbiden_chars = selections.validate_list(
      items)
  if invalid_article_names:
    return {
        "status": "200",
        "success": False,
        "items": {
            'valid': valid_article_names,
            'invalid': invalid_article_names,
            "forbiden_chars": forbiden_chars
        }
    }
  return {"status": "200", "success": True, "items": {}}
