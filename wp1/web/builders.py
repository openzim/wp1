import flask
import importlib
import logging

from wp1.credentials import CREDENTIALS, ENV
from wp1.environment import Environment
from wp1.exceptions import ObjectNotFoundError, UserNotAuthorizedError, ZimFarmError
import wp1.logic.builder as logic_builder
import wp1.logic.selection as logic_selection
from wp1 import queues
from wp1 import zimfarm
from wp1.web import authenticate
from wp1.web.db import get_db
from wp1.web.redis import get_redis
from wp1.web.storage import get_storage

builders = flask.Blueprint('builders', __name__)

logger = logging.getLogger(__name__)


def _create_or_update_builder(data, builder_id=None):
  list_name = data['name']
  project = data['project']
  model = data['model']
  params = data['params']

  if not list_name or not project or not model or not params:
    return 'Missing list_name or project or model or params', 400

  builder_module = importlib.import_module(model)
  Builder = getattr(builder_module, 'Builder')
  if Builder is None:
    logger.warn('Could not find model: %s', model)
    flask.abort(400)

  builder = Builder()
  valid_values, invalid_values, errors = builder.validate(project=project,
                                                          **params)
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

  selection_errors = logic_builder.latest_selections_with_errors(
      wp10db, builder_id)
  res = builder.to_web_dict()
  res.update(selection_errors=selection_errors)
  return flask.jsonify(res)


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


@builders.route('/<builder_id>/zim', methods=['POST'])
@authenticate
def create_zim_file_for_builder(builder_id):
  redis = get_redis()
  wp10db = get_db('wp10db')
  s3 = get_storage()

  user_id = flask.session['user']['identity']['sub']

  data = flask.request.get_json()
  desc = data.get('description')
  if not desc:
    return flask.jsonify(
        {'error_messages': 'Description is required for ZIM file'}), 400
  long_desc = data.get('long_description')

  try:
    task_id = logic_builder.schedule_zim_file(s3,
                                              redis,
                                              wp10db,
                                              builder_id,
                                              user_id=user_id,
                                              description=desc,
                                              long_description=long_desc)
  except ObjectNotFoundError:
    return flask.jsonify(
        {'error_messages': ['No builder found with id = %s' % builder_id]}), 404
  except UserNotAuthorizedError:
    return flask.jsonify({
        'error_messages': [
            'Not authorized to perform this operation on that builder'
        ]
    }), 403
  except ZimFarmError as e:
    error_messages = [str(e)]
    if e.__cause__:
      error_messages.append(str(e.__cause__))
    return flask.jsonify({'error_messages': error_messages}), 500

  return '', 204


@builders.route('/<builder_id>/zim/status')
def zimfarm_status(builder_id):
  wp10db = get_db('wp10db')
  return flask.jsonify(logic_builder.zim_file_status_for(wp10db, builder_id))


@builders.route('/zim/status', methods=['POST'])
def update_zimfarm_status():
  token = CREDENTIALS[ENV].get('ZIMFARM', {}).get('hook_token')
  provided_token = flask.request.args.get('token')
  if token and provided_token != token:
    flask.abort(403)

  data = flask.request.get_json()
  task_id = data.get('_id')
  if task_id is None:
    flask.abort(400)

  wp10db = get_db('wp10db')

  if data.get('status') == 'failed':
    # Update the status as FAILED and return.
    logic_selection.update_zimfarm_task(wp10db, task_id, 'FAILED')
    return '', 204

  files = data.get('files', {})
  for key, value in files.items():
    if value['status'] == 'uploaded':
      # Update the status as FILE_READY and return.
      logic_selection.update_zimfarm_task(wp10db,
                                          task_id,
                                          'FILE_READY',
                                          set_updated_now=True)
      return '', 204

  found = logic_selection.update_zimfarm_task(wp10db, task_id, 'ENDED')
  if found:
    # If the task_id exists, start polling for the file to be ready.
    redis = get_redis()
    queues.poll_for_zim_file_status(redis, task_id)
  return '', 204


@builders.route('/<builder_id>/zim/latest')
def latest_zim_file_for_builder(builder_id):
  wp10db = get_db('wp10db')

  url = logic_builder.latest_zim_file_url_for(wp10db, builder_id)
  if not url:
    flask.abort(404)

  return flask.redirect(url, code=302)
