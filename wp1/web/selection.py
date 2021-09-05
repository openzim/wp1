import flask

from wp1.constants import CONTENT_TYPE_TO_EXT
import wp1.logic.builder as logic_builder
from wp1 import queues
from wp1.selection.models.simple_builder import SimpleBuilder
from wp1.web import authenticate
from wp1.web.db import get_db
from wp1.web.redis import get_redis
from wp1.web.storage import get_storage

selection = flask.Blueprint('selection', __name__)


@selection.route('/simple', methods=['POST'])
@authenticate
def create():
  data = flask.request.get_json()
  list_name = data['name']
  articles = data['articles']
  project = data['project']
  params = {'list': articles.split('\n')}
  if not articles or not list_name or not project:
    flask.abort(400)
  simple_builder = SimpleBuilder()
  valid_names, invalid_names, errors = simple_builder.validate(**params)
  if invalid_names:
    return flask.jsonify({
        'success': False,
        'items': {
            'valid': valid_names,
            'invalid': invalid_names,
            'errors': errors
        }
    })

  wp10db = get_db('wp10db')
  redis = get_redis()

  user_id = flask.session['user']['identity']['sub']
  builder_id = logic_builder.save_builder(wp10db, list_name, user_id, project,
                                          articles)
  queues.enqueue_materialize(redis, SimpleBuilder, builder_id,
                             'text/tab-separated-values')
  return flask.jsonify({'success': True, 'items': {}})


@selection.route('/simple/lists')
@authenticate
def get_list_data():
  wp10db = get_db('wp10db')
  user_id = flask.session['user']['identity']['sub']
  builders = logic_builder.get_builders_with_selections(wp10db, user_id)
  return flask.jsonify({'builders': builders})
