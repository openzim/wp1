import logging

from redis import Redis

logger = logging.getLogger(__name__)

try:
  from wp1.credentials import ENV, CREDENTIALS
except ImportError:
  logger.exception('The file credentials.py must be populated manually in '
                   'order to connect to Redis')
  ENV = None
  CREDENTIALS = None


def connect():
  creds = CREDENTIALS[ENV]['REDIS']
  return Redis(**creds)


def gen_redis_log_key(*, project: str | bytes, namespace: str | bytes,
                      action: str | bytes, article: str | bytes) -> str:
  to_str = lambda x: x.decode("utf-8") if isinstance(x, bytes) else x
  return f"wp1:logs:{to_str(project)}:{to_str(namespace)}:{to_str(action)}:{to_str(article)}"
