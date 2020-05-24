import logging

import flask
from redis import Redis

logger = logging.getLogger(__name__)

try:
  from wp1.credentials import CREDENTIALS, ENV
except ImportError:
  logger.exception('The file credentials.py must be populated manually in '
                   'order to connect to the required databases')
  CREDENTIALS = None
  ENV = None


def has_redis():
  return hasattr(flask.g, 'redis')


def get_redis():
  if not has_redis():
    creds = CREDENTIALS[ENV]['REDIS']
    setattr(flask.g, 'redis', Redis(**creds))
  return getattr(flask.g, 'redis')
