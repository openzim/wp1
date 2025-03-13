import logging

from redis import Redis
from rq import Queue

from wp1.environment import Environment
from wp1 import constants
from wp1 import tables
import wp1.logic.project as logic_project

logger = logging.getLogger(__name__)

try:
  from wp1.credentials import ENV, CREDENTIALS
except ImportError:
  logger.exception('The file credentials.py must be populated manually in '
                   'order to connect to Redis')
  CREDENTIALS = None
  ENV = None


def main():
  logging.basicConfig(level=logging.INFO)

  creds = CREDENTIALS[ENV]['REDIS']

  upload_q = Queue('upload', connection=Redis(**creds))

  if ENV == Environment.PRODUCTION:
    logger.info('Enqueuing global table upload')
    upload_q.enqueue(tables.upload_global_table,
                     job_timeout=constants.JOB_TIMEOUT)

  logger.info('Enqueuing global project count')
  upload_q.enqueue(logic_project.update_global_project_count,
                   job_timeout=constants.JOB_TIMEOUT)


if __name__ == '__main__':
  main()
