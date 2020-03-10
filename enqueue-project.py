import logging
import sys

from redis import Redis
from rq import Queue

from wp1 import constants
from wp1.environment import Environment
from wp1 import logs
import wp1.logic.project as logic_project
from wp1 import tables

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

  update_q = Queue('update', connection=Redis(**creds))
  upload_q = Queue('upload', connection=Redis(**creds))

  # Job methods expect project names as bytes.
  project_names = [n.encode('utf-8') for n in sys.argv[1:]]
  logger.debug(project_names)

  for project_name in project_names:
    logger.info('Enqueuing update %s', project_name)
    update_job = update_q.enqueue(logic_project.update_project_by_name,
                                  project_name,
                                  job_timeout=constants.JOB_TIMEOUT)
    if ENV == Environment.PRODUCTION:
      logger.info('Enqueuing upload (dependent) %s', project_name)
      upload_q.enqueue(tables.upload_project_table,
                       project_name,
                       depends_on=update_job,
                       job_timeout=constants.JOB_TIMEOUT)
      logger.info('Enqueuing log upload (dependent) %s', project_name)
      upload_q.enqueue(logs.update_log_page_for_project,
                       project_name,
                       depends_on=update_job,
                       job_timeout=constants.JOB_TIMEOUT)
    else:
      logger.warning('Skipping enqueuing the upload job because environment is '
                     'not PRODUCTION')


if __name__ == '__main__':
  main()
