import logging
import sys

from wp1 import app_logging, queues
from wp1.redis_db import connect as redis_connect

logger = logging.getLogger(__name__)


def main():
  app_logging.configure_logging()

  # Job methods expect project names as bytes.
  project_names = [n.encode('utf-8') for n in sys.argv[1:]]
  logger.debug(project_names)

  redis = redis_connect()
  queues.enqueue_multiple_projects(redis, project_names)


if __name__ == '__main__':
  main()
