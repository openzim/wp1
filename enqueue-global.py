import logging

from redis import Redis
from rq import Queue

import wp1.logic.project as logic_project
from wp1 import app_logging, constants, tables
from wp1.credentials import CREDENTIALS, ENV
from wp1.environment import Environment

logger = logging.getLogger(__name__)


def main():
  app_logging.configure_logging()

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
