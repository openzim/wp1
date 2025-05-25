import logging

from wp1 import app_logging, queues
from wp1.redis_db import connect as redis_connect
from wp1.wp10_db import connect as wp10_connect

logger = logging.getLogger(__name__)


def main():
  app_logging.configure_logging()

  wp10db = wp10_connect()
  redis = redis_connect()
  queues.enqueue_all_projects(redis, wp10db)


if __name__ == '__main__':
  main()
