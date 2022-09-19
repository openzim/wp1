import flask
import importlib
import logging

import wp1.logic.builder as logic_builder
from wp1 import queues
from wp1.web import authenticate
from wp1.web.db import get_db
from wp1.web.redis import get_redis

builders = flask.Blueprint('builders', __name__)

logger = logging.getLogger(__name__)


def _create_or_update_builder(data, builder_id=None):
  list_name = data['name']
  project = data['project']
  model = data['model']
  params = data['params']

  if not list_name or not project or not model or not params:
    flask.abort(400)

  builder_module = importlib.import_module(model)
  Builder = getattr(builder_module, 'Builder')
  if Builder is None:
    logger.warn('Could not find model: %s', model)
    flask.abort(400)

  builder = Builder()
  valid_values, invalid_values, errors = builder.validate(**params)
  if invalid_values or errors:
    return flask.jsonify({
        'success': False,
        'items': {
            'valid': valid_values,
            'invalid': invalid_values,
            'errors': errors,
        }
    })

  wp10db = get_db('wp10db')
  redis = get_redis()

  user_id = flask.session['user']['identity']['sub']
  builder_id = logic_builder.create_or_update_builder(wp10db,
                                                      list_name,
                                                      user_id,
                                                      project,
                                                      params,
                                                      model,
                                                      builder_id=builder_id)
  # Either the builder was not found or the user ID was not correct. Nothing was
  # updated, return 404.
  if builder_id is None:
    flask.abort(404)

  # The builder has been updated. Enqueue a task to materialize selections and
  # update the current version.
  queues.enqueue_materialize(redis, Builder, builder_id,
                             'text/tab-separated-values')
  return flask.jsonify({'success': True, 'items': {}})


@builders.route('/', methods=['POST'])
@authenticate
def create_builder():
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


@builders.route('/<builder_id>/delete', methods=['POST'])
@authenticate
def delete_builder(builder_id):
  wp10db = get_db('wp10db')
  user_id = flask.session['user']['identity']['sub']

  status = logic_builder.delete_builder(wp10db, user_id, builder_id)

  if not status['db_delete_success']:
    flask.abort(404)

  return {'status': '204'}


@builders.route('/<builder_id>/selection/latest.<ext>')
def latest_selection_for_builder(builder_id, ext):
  wp10db = get_db('wp10db')

  url = logic_builder.latest_selection_url(wp10db, builder_id, ext)
  if not url:
    flask.abort(404)

  return flask.redirect(url, code=302)
