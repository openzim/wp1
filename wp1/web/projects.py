from wp1.web import authenticate
import attr
import flask
import logging

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


@projects.route('/<project_name>')
def project(project_name):
  wp10db = get_db('wp10db')
  project_name_bytes = project_name.encode('utf-8')
  project = logic_project.get_project_by_name(wp10db, project_name_bytes)
  if project is None:
    return flask.abort(404)

  return flask.jsonify(project.to_web_dict())


@projects.route('/<project_name>/table')
def table(project_name):
  wp10db = get_db('wp10db')
  project_name_bytes = project_name.encode('utf-8')
  project = logic_project.get_project_by_name(wp10db, project_name_bytes)
  if project is None:
    return flask.abort(404)

  data = tables.generate_project_table_data(wp10db, project_name_bytes)
  logger = logging.getLogger(__name__)
  logger.info('Generated table data: %s', data)

  data = tables.convert_table_data_for_web(data)
  logger.info('Converted table data: %s', data)

  return flask.jsonify({'table_data': data})


@projects.route('/<project_name>/category_links')
def category_links(project_name):
  wp10db = get_db('wp10db')
  project_name_bytes = project_name.encode('utf-8')
  project = logic_project.get_project_by_name(wp10db, project_name_bytes)
  if project is None:
    return flask.abort(404)

  data = tables.generate_project_table_data(wp10db, project_name_bytes)
  data = tables.get_project_category_links(data)

  return flask.jsonify(data)


@projects.route('/<project_name>/category_links/sorted')
def category_links_sorted(project_name):
  wp10db = get_db('wp10db')
  project_name_bytes = project_name.encode('utf-8')
  project = logic_project.get_project_by_name(wp10db, project_name_bytes)
  if project is None:
    return flask.abort(404)
  data = tables.generate_project_table_data(wp10db, project_name_bytes)
  data = tables.get_project_category_links(data, sort=True)

  return flask.jsonify(data)


@projects.route('/<project_name>/articles')
def articles(project_name):
  wp10db = get_db('wp10db')
  project_name_bytes = project_name.encode('utf-8')
  project = logic_project.get_project_by_name(wp10db, project_name_bytes)
  if project is None:
    return flask.abort(404)

  project_b_name_bytes = None
  quality_b = None
  importance_b = None
  project_b_name = flask.request.args.get('projectB')
  if project_b_name is not None:
    project_b_name_bytes = project_b_name.encode('utf-8')
    project_b = logic_project.get_project_by_name(wp10db, project_b_name_bytes)
    if project_b is None:
      return flask.abort(404)

    quality_b = flask.request.args.get('qualityB')
    importance_b = flask.request.args.get('importanceB')

  quality = flask.request.args.get('quality')
  importance = flask.request.args.get('importance')
  page = flask.request.args.get('page')
  page_int = 1
  limit = flask.request.args.get('numRows')
  limit_int = 100
  if page is not None:
    try:
      page_int = int(page)
    except ValueError:
      return flask.abort(400)
    if page_int < 1:
      return flask.abort(400)

  if limit is not None:
    try:
      limit_int = int(limit)
    except ValueError:
      return flask.abort(400)
    if limit_int < 1:
      return flask.abort(400)
    if limit_int > 500:
      limit_int = 500

  if quality:
    quality = quality.encode('utf-8')
  if importance:
    importance = importance.encode('utf-8')

  article_pattern = flask.request.args.get('articlePattern')

  total = logic_rating.get_project_rating_count_by_type(
      wp10db,
      project_name_bytes,
      quality=quality,
      importance=importance,
      project_b_name=project_b_name_bytes,
      quality_b=quality_b,
      importance_b=importance_b,
      pattern=article_pattern)
  total_pages = total // limit_int + (1 if total % limit_int != 0 else 0)

  start = limit_int * (page_int - 1) + 1
  end = min(limit_int - 1 + start, total)
  display = {'start': start, 'end': end, 'num_rows': limit_int}

  articles = logic_rating.get_project_rating_by_type(
      wp10db,
      project_name_bytes,
      quality=quality,
      importance=importance,
      project_b_name=project_b_name_bytes,
      quality_b=quality_b,
      importance_b=importance_b,
      pattern=article_pattern,
      page=page,
      limit=limit_int)

  if project_b_name is None:
    output_articles = list(article.to_web_dict(wp10db) for article in articles)
  else:
    output_articles = list(
        (a[0].to_web_dict(wp10db), a[1].to_web_dict(wp10db)) for a in articles)

  output = {
      'pagination': {
          'page': page or 1,
          'total_pages': total_pages,
          'total': total,
          'display': display,
      },
      'articles': output_articles,
  }
  return flask.jsonify(output)


@projects.route('/<project_name>/update', methods=['POST'])
@authenticate
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
    except (AttributeError, ValueError):
      # AttributeError: The values are not bytes and can't be decoded.
      # ValueError: The values are not castable to int.
      progress = 0
      work = 0
    job = {'progress': progress, 'total': work}

  return flask.jsonify({'queue': queue_status, 'job': job})
