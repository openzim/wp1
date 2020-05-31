import attr
import flask

from wp1.constants import PAGE_SIZE
from wp1.web.db import get_db
from wp1.web.redis import get_redis
import wp1.logic.project as logic_project
import wp1.logic.rating as logic_rating
from wp1 import queues
from wp1 import tables

projects = flask.Blueprint('projects', __name__)


@projects.route('/')
def list_():
  wp10db = get_db('wp10db')
  projects = logic_project.list_all_projects(wp10db)
  return flask.jsonify(list(project.to_web_dict() for project in projects))


@projects.route('/count')
def count():
  wp10db = get_db('wp10db')
  count = logic_project.count_projects(wp10db)
  return flask.jsonify({'count': count})


@projects.route('/<project_name>/table')
def table(project_name):
  wp10db = get_db('wp10db')
  project_name_bytes = project_name.encode('utf-8')
  project = logic_project.get_project_by_name(wp10db, project_name_bytes)
  if project is None:
    return flask.abort(404)

  data = tables.generate_project_table_data(wp10db, project_name_bytes)
  data = tables.convert_table_data_for_web(data)

  return flask.jsonify({'table_data': data})


@projects.route('/<project_name>/articles')
def articles(project_name):
  wp10db = get_db('wp10db')
  project_name_bytes = project_name.encode('utf-8')
  project = logic_project.get_project_by_name(wp10db, project_name_bytes)
  if project is None:
    return flask.abort(404)

  quality = flask.request.args.get('quality')
  importance = flask.request.args.get('importance')
  page = flask.request.args.get('page')
  if page is not None:
    try:
      page_int = int(page)
    except ValueError:
      # Non-integer page number
      return flask.abort(400)
    if page_int < 1:
      # Negative page number
      return flask.abort(400)

  if quality:
    quality = quality.encode('utf-8')
  if importance:
    importance = importance.encode('utf-8')

  total = logic_rating.get_project_rating_count_by_type(wp10db,
                                                        project_name_bytes,
                                                        quality=quality,
                                                        importance=importance)
  total_pages = total // PAGE_SIZE + 1 if total % PAGE_SIZE != 0 else 0

  articles = logic_rating.get_project_rating_by_type(wp10db,
                                                     project_name_bytes,
                                                     quality=quality,
                                                     importance=importance,
                                                     page=page)

  output = {
      'pagination': {
          'page': page or 1,
          'total_pages': total_pages,
          'total': total
      },
      'articles': list(article.to_web_dict() for article in articles),
  }
  return flask.jsonify(output)


@projects.route('/<project_name>/update', methods=['POST'])
def update(project_name):
  wp10db = get_db('wp10db')
  project_name_bytes = project_name.encode('utf-8')
  project = logic_project.get_project_by_name(wp10db, project_name_bytes)
  if project is None:
    return flask.abort(404)

  redis = get_redis()

  update_time = queues.next_update_time(redis, project_name_bytes)
  if update_time is not None:
    return flask.jsonify({'next_update_time': update_time}), 400

  queues.enqueue_single_project(redis, project_name_bytes, manual=True)
  next_update_time = queues.mark_project_manual_update_time(
      redis, project_name_bytes)
  return flask.jsonify({'next_update_time': next_update_time})


@projects.route('/<project_name>/update/time')
def update_time(project_name):
  wp10db = get_db('wp10db')
  project_name_bytes = project_name.encode('utf-8')
  project = logic_project.get_project_by_name(wp10db, project_name_bytes)
  if project is None:
    return flask.abort(404)

  redis = get_redis()

  update_time = queues.next_update_time(redis, project_name_bytes)
  return flask.jsonify({'next_update_time': update_time}), 200


@projects.route('/<project_name>/update/progress')
def update_progress(project_name):
  wp10db = get_db('wp10db')
  project_name_bytes = project_name.encode('utf-8')
  project = logic_project.get_project_by_name(wp10db, project_name_bytes)
  if project is None:
    return flask.abort(404)

  redis = get_redis()

  progress, work = logic_project.get_project_progress(redis, project_name_bytes)
  queue_status = queues.get_project_queue_status(redis, project_name_bytes)

  if progress is None or work is None:
    job = None
  else:
    try:
      progress = int(progress.decode('utf-8'))
      work = int(work.decode('utf-8'))
    except AttributeError, ValueError:
      # AttributeError: The values are not bytes and can't be decoded.
      # ValueError: The values are not castable to int.
      progress = 0
      work = 0
    job = {'progress': progress, 'total': work}

  return flask.jsonify({'queue': queue_status, 'job': job})
