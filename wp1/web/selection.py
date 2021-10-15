import flask

from wp1.constants import CONTENT_TYPE_TO_EXT
import wp1.logic.builder as logic_builder

from wp1.web import authenticate
from wp1.web.db import get_db
from wp1.web.storage import get_storage

selection = flask.Blueprint('selection', __name__)


@selection.route('/simple/lists')
@authenticate
def get_list_data():
  wp10db = get_db('wp10db')
  user_id = flask.session['user']['identity']['sub']
  builders = logic_builder.get_builders_with_selections(wp10db, user_id)
  return flask.jsonify({'builders': builders})
