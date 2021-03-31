from datetime import datetime, timedelta

import flask

from wp1.timestamp import utcnow
from wp1.web.redis import get_redis

dev_projects = flask.Blueprint('dev_projects', __name__)

UPDATE_DURATION_MINS = 5


def clear_project_progress(redis, project_name):
  key = _project_progress_key(project_name)
  redis.delete(key)


def enqueue_single_project(redis, project_name):
  clear_project_progress(redis, project_name)


def _manual_key(project_name):
  return b'DEV_manual_key:%s' % project_name


def _project_progress_key(project_name):
  return b'DEV_progress:%s' % project_name


def mark_project_manual_update_time(redis, project_name):
  key = _manual_key(project_name)
  ts = (utcnow() +
        timedelta(minutes=UPDATE_DURATION_MINS)).strftime('%Y-%m-%d %H:%M UTC')
  redis.setex(key, timedelta(minutes=UPDATE_DURATION_MINS), value=ts)
  return ts


def next_update_time(redis, project_name):
  key = _manual_key(project_name)
  ts = redis.get(key)
  if ts is not None:
    ts = ts.decode('utf-8')
  return ts


def _progress_secs(dt):
  # The progress is the number of seconds that have passed in the first minute of update time
  secs = (dt - timedelta(minutes=UPDATE_DURATION_MINS - 1)) - utcnow()
  if secs.seconds > 60 or secs.seconds < 0:
    return 60
  return 60 - secs.seconds


def get_project_progress(redis, project_name):
  ts = next_update_time(redis, project_name)
  if ts is None:
    return None, None

  dt = datetime.strptime(ts, '%Y-%m-%d %H:%M UTC')
  progress = _progress_secs(dt)

  if project_name == b'Water' and progress > 10:
    return 10, 60
  return progress, 60


def get_project_queue_status(redis, project_name):
  progress, work = get_project_progress(redis, project_name)
  if not progress:
    return None
  elif progress < 5:
    return 'queued'
  elif progress > 10 and project_name == b'Water':
    return 'failed'
  if progress > 50:
    return 'finished'

  return 'started'


@dev_projects.route('/<project_name>/update', methods=['POST'])
def update(project_name):
  project_name_bytes = project_name.encode('utf-8')
  redis = get_redis()

  update_time = next_update_time(redis, project_name_bytes)
  if update_time is not None:
    return flask.jsonify({'next_update_time': update_time}), 400

  enqueue_single_project(redis, project_name_bytes)
  next_time = mark_project_manual_update_time(redis, project_name_bytes)
  return flask.jsonify({'next_update_time': next_time})


@dev_projects.route('/<project_name>/update/time')
def update_time(project_name):
  project_name_bytes = project_name.encode('utf-8')
  redis = get_redis()

  update_time = next_update_time(redis, project_name_bytes)
  return flask.jsonify({'next_update_time': update_time}), 200


@dev_projects.route('/<project_name>/update/progress')
def update_progress(project_name):
  project_name_bytes = project_name.encode('utf-8')
  redis = get_redis()

  progress, work = get_project_progress(redis, project_name_bytes)
  queue_status = get_project_queue_status(redis, project_name_bytes)

  if progress is None or work is None:
    job = None
  else:
    job = {'progress': progress, 'total': work}

  return flask.jsonify({'queue': queue_status, 'job': job})
