import io

import flask

import wp1.logic.selection as logic_selection
from wp1.web import authenticate
from wp1.web.db import get_db
from wp1.web.storage import get_storage

selection = flask.Blueprint('selection', __name__)


@selection.route('/simple', methods=['POST'])
@authenticate
def create():
  data = flask.request.get_json()
  list_name = data['list_name']
  articles = data['articles']
  project = data['project']
  if not articles or not list_name or not project:
    flask.abort(400)

  # Validate the article names
  valid_names, invalid_names, forbiden_chars = logic_selection.validate_list(
      articles)
  if invalid_names:
    # If there are invalid names, return the whole thing to the frontend
    return flask.jsonify({
        "success": False,
        "items": {
            'valid': valid_names,
            'invalid': invalid_names,
            "forbiden_chars": forbiden_chars
        }
    })

  # All valid, time to upload to s3 and store in the application database.
  s3 = get_storage()
  wp10db = get_db('wp10db')
  user_id = flask.session['user']['identity']['sub']
  logic_selection.persist_simple_list(wp10db, s3, list_name, user_id, project,
                                      valid_names)

  return flask.jsonify({"success": True, "items": {}})
