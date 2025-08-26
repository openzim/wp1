import logging

import flask

import wp1.logic.builder as logic_builder
import wp1.logic.selection as logic_selection
import wp1.logic.zim_files as logic_zim_tasks
import wp1.logic.zim_schedules as logic_zim_schedules
from wp1 import queues
from wp1.constants import EXT_TO_CONTENT_TYPE
from wp1.credentials import CREDENTIALS, ENV
from wp1.exceptions import (ObjectNotFoundError, UserNotAuthorizedError,
                            ZimFarmError, ZimFarmTooManyArticlesError)
from wp1.web import authenticate, emails
from wp1.web.db import get_db
from wp1.web.redis import get_redis
from wp1.web.storage import get_storage
from wp1.zimfarm import MAX_ZIMFARM_ARTICLE_COUNT

builders = flask.Blueprint('builders', __name__)

logger = logging.getLogger(__name__)


def _create_or_update_builder(wp10db, data, builder_id=None):
  list_name = data['name']
  project = data['project']
  model = data['model']
  params = data['params']

  if not list_name or not project or not model or not params:
    return 'Missing list_name or project or model or params', 400

  try:
    builder_cls = logic_builder.get_builder_module_class(model)
  except ImportError as e:
    logger.warning(str(e))
    flask.abort(400)

  builder_obj = builder_cls()
  valid_values, invalid_values, errors = builder_obj.validate(project=project,
                                                              wp10db=wp10db,
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

  builder = logic_builder.get_builder(wp10db, builder_id)

  # The builder has been updated. Enqueue a task to materialize selections and
  # update the current version.
  queues.enqueue_materialize(redis, builder_cls, builder,
                             'text/tab-separated-values')
  return flask.jsonify({'success': True, 'items': {}})


@builders.route('/', methods=['POST'])
@authenticate
def create_builder():
  wp10db = get_db('wp10db')
  data = flask.request.get_json()
  return _create_or_update_builder(wp10db, data)


@builders.route('/<builder_id>', methods=['POST'])
@authenticate
def update_builder(builder_id):
  wp10db = get_db('wp10db')
  data = flask.request.get_json()
  return _create_or_update_builder(wp10db, data, builder_id)


@builders.route('/<builder_id>')
@authenticate
def get_builder(builder_id):
  wp10db = get_db('wp10db')
  try:
    builder = logic_builder.get_builder(wp10db, builder_id)
  except ObjectNotFoundError:
    flask.abort(404)

  # Don't return the builder unless it belongs to this user.
  user = flask.session.get('user')
  builder_user_id = builder.b_user_id.decode('utf-8')
  logged_in_user_id = str(user['identity']['sub'])
  if builder_user_id != logged_in_user_id:
    logger.warning(
        'User id mismatch, user %r tried to access builder %r which is owned by user %r',
        logged_in_user_id, builder_id, builder_user_id)
    flask.abort(401, 'Unauthorized')

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
<<<<<<< HEAD

  try:
    status = logic_builder.delete_builder(wp10db, user_id, builder_id)
  except UserNotAuthorizedError as e:
    flask.abort(403)
  except ObjectNotFoundError:
    flask.abort(404)
=======
  status = logic_builder.delete_builder(wp10db, user_id, builder_id)
>>>>>>> d67c9a1 (feat(email): Add email confirmation feature for ZIM file notifications)

  if not status['db_delete_success']:
    return flask.jsonify(
        {'error_messages': ['Failed to delete builder from database']}), 500

  return {'status': '204'}


@builders.route('/<builder_id>/selection/latest.<ext>')
def latest_selection_for_builder(builder_id, ext):
  wp10db = get_db('wp10db')

  url = logic_builder.latest_selection_url(wp10db, builder_id, ext)
  if not url:
    flask.abort(404)

  return flask.redirect(url, code=302)


@builders.route('/<builder_id>/selection/latest/article_count')
@authenticate
def latest_selection_article_count_for_builder(builder_id):
  wp10db = get_db('wp10db')

  user_id = flask.session['user']['identity']['sub']
  builder = logic_builder.get_builder(wp10db, builder_id)
  if builder.b_user_id.decode('utf-8') != user_id:
    return flask.jsonify({
        'error_messages': [
            'Cannot get article count for a selection that does not belong to you'
        ]
    }), 403

  selection = logic_builder.latest_selection_for(wp10db, builder_id,
                                                 EXT_TO_CONTENT_TYPE['tsv'])
  if not selection:
    flask.abort(404)

  return flask.jsonify({
      'selection': {
          'id': selection.s_id.decode('utf-8'),
          'article_count': selection.s_article_count,
          'max_article_count': MAX_ZIMFARM_ARTICLE_COUNT,
      }
  })


@builders.route('/<builder_id>/zim', methods=['POST'])
@authenticate
def create_zim_file_for_builder(builder_id):
  redis = get_redis()
  wp10db = get_db('wp10db')

  user_id = flask.session['user']['identity']['sub']
  data = flask.request.get_json()
  title = data.get('title')
  desc = data.get('description')
  long_desc = data.get('long_description')
  scheduled_repetitions = data.get('scheduled_repetitions')

  error_messages = []
  if not title:
    error_messages.append('Title is required for ZIM file')

  if not desc:
    error_messages.append('Description is required for ZIM file')

  if error_messages:
    return flask.jsonify({'error_messages': error_messages}), 400

  if scheduled_repetitions not in (None, {}):
    if not (isinstance(scheduled_repetitions, dict) and
            all(k in scheduled_repetitions for k in (
                "repetition_period_in_months",
                "number_of_repetitions",
            ))):
      return 'Invalid or missing fields in scheduled_repetitions', 400

  # Set scheduled_repetitions to None if it's an empty dict
  if scheduled_repetitions == {}:
    scheduled_repetitions = None

  try:
    logic_builder.handle_zim_generation(
        redis,
        wp10db,
        builder_id,
        user_id=user_id,
        title=title,
        description=desc,
        long_description=long_desc,
        scheduled_repetitions=scheduled_repetitions)
  except ObjectNotFoundError:
    return flask.jsonify(
        {'error_messages': ['No builder found with id = %s' % builder_id]}), 404
  except UserNotAuthorizedError:
    return flask.jsonify({
        'error_messages': [
            'Not authorized to perform this operation on that builder'
        ]
    }), 403
  except ZimFarmTooManyArticlesError as e:
    return flask.jsonify({'error_messages': [e.user_message()]}), 400
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

  if data.get('status') in ('failed', 'cancelled', None):
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

      zim_task = logic_zim_tasks.get_zim_task_by_task_id(wp10db, task_id)
      zim_schedule = logic_zim_schedules.get_zim_schedule(
          wp10db, zim_task.z_zim_schedule_id)
      if zim_schedule is None:
        return 'Error: ZIM not found for task_id %s' % task_id, 500

      if zim_schedule.s_remaining_generations is not None and zim_schedule.s_remaining_generations > 0:
        emails.respond_to_zim_task_completed(wp10db, zim_task, zim_schedule)
      return '', 204


@builders.route('/<builder_id>/zim/latest')
def latest_zim_file_for_builder(builder_id):
  wp10db = get_db('wp10db')

  url = logic_builder.latest_zim_file_url_for(wp10db, builder_id)
  if not url:
    flask.abort(404)

  return flask.redirect(url, code=302)


@builders.route('/<builder_id>/schedule', methods=['DELETE'])
@authenticate
def delete_schedule_for_builder(builder_id):
  """Delete an active recurring schedule for a builder."""
  redis = get_redis()
  wp10db = get_db('wp10db')

  user_id = flask.session['user']['identity']['sub']

  # Get the builder and verify ownership
  builder = logic_builder.get_builder(wp10db, builder_id.encode('utf-8'))
  if not builder:
    return flask.jsonify({'error_messages': ['Builder not found']}), 404

  builder_user_id = builder.b_user_id.decode('utf-8')
  if str(user_id) != builder_user_id:
    return flask.jsonify(
        {'error_messages': ['Not authorized to modify this builder']}), 403

  # Find the active recurring schedule
  active_schedule = logic_zim_schedules.find_active_recurring_schedule_for_builder(
      wp10db, builder_id.encode('utf-8'))
  if not active_schedule:
    return flask.jsonify(
        {'error_messages': ['No active recurring schedule found']}), 404

  # Delete the schedule
  deleted = logic_zim_schedules.delete_zim_schedule(redis, wp10db,
                                                    active_schedule.s_id)
  if not deleted:
    return flask.jsonify({'error_messages': ['Failed to delete schedule']}), 500

  return '', 204
