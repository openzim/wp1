import flask
from wp1.web import authenticate
import wp1.logic.selection as selections

selection = flask.Blueprint('selection', __name__)


@selection.route('/simple', methods=['POST'])
def get_article_names():
  list_name = flask.request.get_json()['list_name']
  items = flask.request.get_json()['article_name']
  if not items or not list_name:
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
