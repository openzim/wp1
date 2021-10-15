import flask

import wp1.logic.builder as logic_builder
from wp1 import queues
from wp1.selection.models.simple_builder import SimpleBuilder
from wp1.web import authenticate
from wp1.web.db import get_db
from wp1.web.redis import get_redis

builders = flask.Blueprint('builders', __name__)


def _create_or_update_builder(data, builder_id=None):
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
  print('user id: %s' % user_id)
  is_update = builder_id is not None
  builder_id = logic_builder.create_or_update_builder(wp10db, list_name,
                                                      user_id, project,
                                                      articles, builder_id)
  # Either the builder was not found or the user ID was not correct. Nothing was
  # updated, return 404.
  if builder_id is None:
    flask.abort(404)

  if not is_update:
    queues.enqueue_materialize(redis, SimpleBuilder, builder_id,
                               'text/tab-separated-values')
  return flask.jsonify({'success': True, 'items': {}})


@builders.route('/', methods=['POST'])
@authenticate
def create():
  data = flask.request.get_json()
  return _create_or_update_builder(data)


@builders.route('/<builder_id>', methods=['POST'])
@authenticate
def update_builder(builder_id):
  data = flask.request.get_json()
  return _create_or_update_builder(data, builder_id)


@builders.route('/<builder_id>')
@authenticate
def get_builder(builder_id):
  wp10db = get_db('wp10db')
  builder = logic_builder.get_builder(wp10db, builder_id)
  if not builder:
    flask.abort(404)

  # Don't return the builder unless it belongs to this user.
  user = flask.session.get('user')
  if builder.b_user_id != user['identity']['sub']:
    flask.abort(404)

  return flask.jsonify(builder.to_web_dict())
