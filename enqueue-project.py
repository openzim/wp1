import sys

from redis import Redis
from rq import Queue

from wp1 import constants
import wp1.logic.project as logic_project
from wp1 import tables


def main():
  update_q = Queue('update', connection=Redis(host='redis'))
  upload_q = Queue('upload', connection=Redis(host='redis'))

  # Job methods expect project names as bytes.
  project_names = [n.encode('utf-8') for n in sys.argv[1:]]
  print(project_names)

  for project_name in project_names:
    print('Enqueuing update %s' % project_name)
    update_job = update_q.enqueue(logic_project.update_project_by_name,
                                  project_name,
                                  job_timeout=constants.JOB_TIMEOUT)
    print('Enqueuing upload (dependent) %s' % project_name)
    upload_q.enqueue(tables.upload_project_table,
                     project_name,
                     depends_on=update_job,
                     job_timeout=constants.JOB_TIMEOUT)


if __name__ == '__main__':
  main()
