'''Development overrides for the /v1/projects endpoints.

The functions provided in this file are API compatible with the normal
path as far as the frontend is concerned. However this blueprint has the following features:

- The "lockout" time between updates is 5 minutes instead of 1 hour.
- All updates take 60 seconds, with the progress being 1/60, 2/60 etc as the seconds pass.
- If the update is for the project 'Water', it will fail after 10 seconds.
'''

from datetime import datetime, timedelta

import flask

from wp1.environment import Environment
from wp1.timestamp import utcnow
from wp1.web.redis import get_redis

UPDATE_DURATION_SECS = 5 * 30
ELAPSED_TIME_SECS = 30
BI_DURATION_SECS = UPDATE_DURATION_SECS + ELAPSED_TIME_SECS // 2

try:
  from wp1.credentials import CREDENTIALS
  overlay_settings = CREDENTIALS[Environment.DEVELOPMENT]['OVERLAY']
  UPDATE_DURATION_SECS = overlay_settings.get('update_wait_time_seconds',
                                              UPDATE_DURATION_SECS)
  ELAPSED_TIME_SECS = overlay_settings.get('job_elapsed_time_seconds',
                                           ELAPSED_TIME_SECS)
  BI_DURATION_SECS = overlay_settings.get('basic_income_total_time_seconds',
                                          BI_DURATION_SECS)
except (ImportError, KeyError):
  # The default values were already set before the attempted import so nothing to do
  pass

dev_projects = flask.Blueprint('dev_projects', __name__)


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
  ts = (
      utcnow() +
      timedelta(seconds=UPDATE_DURATION_SECS)).strftime('%Y-%m-%d %H:%M:%S UTC')
  redis.setex(key, timedelta(seconds=UPDATE_DURATION_SECS), value=ts)
  return ts


def next_update_time(redis, project_name):
  key = _manual_key(project_name)
  ts = redis.get(key)
  if ts is not None:
    ts = ts.decode('utf-8')
  return ts


def _progress_secs(dt, project_name):
  # The progress is the number of seconds that have passed in the first minute of update time
  if project_name == b'Basic_Income':
    secs = (dt + timedelta(minutes=2)) - utcnow()
    bi = BI_DURATION_SECS - secs.seconds
    return bi if bi > 0 else BI_DURATION_SECS
  else:
    secs = (dt - timedelta(seconds=UPDATE_DURATION_SECS -
                           ELAPSED_TIME_SECS)) - utcnow()
  if project_name == b'Aesthetics' and secs.seconds >= ELAPSED_TIME_SECS:
    if secs.seconds >= ELAPSED_TIME_SECS * 2 or secs.seconds < 0:
      return ELAPSED_TIME_SECS * 2
    return secs.seconds
  if secs.seconds > ELAPSED_TIME_SECS or secs.seconds < 0:
    return ELAPSED_TIME_SECS
  return ELAPSED_TIME_SECS - secs.seconds


def get_project_progress(redis, project_name):
  ts = next_update_time(redis, project_name)
  if ts is None:
    return None, None

  dt = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S UTC')
  progress = _progress_secs(dt, project_name)

  if project_name == b'Water' and progress >= ELAPSED_TIME_SECS // 4:
    return ELAPSED_TIME_SECS // 4, ELAPSED_TIME_SECS

  if project_name == b'Aesthetics' and progress >= ELAPSED_TIME_SECS:
    return int(ELAPSED_TIME_SECS * 1.2), ELAPSED_TIME_SECS
  return progress, ELAPSED_TIME_SECS


def get_project_queue_status(redis, project_name):
  progress, work = get_project_progress(redis, project_name)
  if not progress:
    return None

  if progress < ELAPSED_TIME_SECS // 4:
    return {'status': 'queued'}

  if progress >= ELAPSED_TIME_SECS // 4 and project_name == b'Water':
    return {'status': 'failed'}

  if progress > ELAPSED_TIME_SECS * 3 // 4:
    ts = next_update_time(redis, project_name)
    if ts is None:
      end = utcnow()

    dt = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S UTC')

    if (project_name == b'Aesthetics' and
        progress < int(ELAPSED_TIME_SECS * 1.2)) or (
            project_name == b'Basic_Income' and progress < BI_DURATION_SECS):
      return {'status': 'started'}

    return {'status': 'finished', 'ended_at': dt - timedelta(minutes=4)}

  return {'status': 'started'}


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
