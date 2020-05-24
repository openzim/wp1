import logging
import sys

from redis import Redis

from wp1 import queues

logger = logging.getLogger(__name__)

try:
  from wp1.credentials import ENV, CREDENTIALS
except ImportError:
  logger.exception('The file credentials.py must be populated manually in '
                   'order to connect to Redis')
  raise


def main():
  logging.basicConfig(level=logging.INFO)

  # Job methods expect project names as bytes.
  project_names = [n.encode('utf-8') for n in sys.argv[1:]]
  logger.debug(project_names)

  creds = CREDENTIALS[ENV]['REDIS']
  redis = Redis(**creds)
  queues.enqueue_multiple_projects(redis, project_names)


if __name__ == '__main__':
  main()
