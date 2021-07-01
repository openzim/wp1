import io

import flask

from wp1.logic.selection import validate_list
from wp1.web.storage import get_storage

selection = flask.Blueprint('selection', __name__)


@selection.route('/', methods=['POST'])
def index():
  name = flask.request.form.get('name')
  if name is None:
    print('name is none')
    flask.abort(400)

  project = flask.request.form.get('project')
  if project is None:
    print('project is none')
    flask.abort(400)

  items = flask.request.form.get('items')
  if items is None:
    print('items is none')
    flask.abort(400)

  valid, invalid = validate_list(items)
  if invalid:
    print('has invalid')
    flask.abort(400)

  s3 = get_storage()

  tsv = '\n'.join(valid).encode('utf-8')
  data = io.BytesIO()
  data.write(tsv)
  data.seek(0)
  s3.upload_fileobj(data, key="test_selection.tsv")
  return 'It worked!', 200
