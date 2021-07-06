import io

import flask

from wp1.web import authenticate
from wp1.web.storage import get_storage
import wp1.logic.selection as logic_selection

selection = flask.Blueprint('selection', __name__)


@selection.route('/simple', methods=['POST'])
def create():
  data = flask.request.get_json()
  list_name = data['list_name']
  articles = data['articles']
  project = data['project']
  if not articles or not list_name or not project:
    flask.abort(400)
  valid_names, invalid_names, forbiden_chars = logic_selection.validate_list(
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

  s3 = get_storage()

  tsv = '\n'.join(valid).encode('utf-8')
  data = io.BytesIO()
  data.write(tsv)
  data.seek(0)
  s3.upload_fileobj(data, key="test_selection.tsv")

  return {"success": True, "items": {}}
