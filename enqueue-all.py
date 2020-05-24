import logging

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

  creds = CREDENTIALS[ENV]['REDIS']
  redis = Redis(**creds)

  queues.enqueue_all_projects(redis)


if __name__ == '__main__':
  main()
