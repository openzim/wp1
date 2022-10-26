import logging

from redis import Redis

from wp1 import queues
from wp1.wp10_db import connect as wp10_connect
from wp1.redis_db import connect as redis_connect

logger = logging.getLogger(__name__)

try:
  from wp1.credentials import ENV, CREDENTIALS
except ImportError:
  logger.exception('The file credentials.py must be populated manually in '
                   'order to connect to Redis')
  raise


def main():
  logging.basicConfig(level=logging.INFO)

  wp10db = wp10_connect()
  redis = redis_connect()
  queues.enqueue_all_projects(redis, wp10db)


if __name__ == '__main__':
  main()
