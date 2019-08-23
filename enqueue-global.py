from redis import Redis
from rq import Queue

from wp1 import constants
from wp1 import tables
import wp1.logic.project as logic_project

def main():
  upload_q = Queue('upload', connection=Redis(host='redis'))

  print('Enqueuing global table upload')
  upload_q.enqueue(tables.upload_global_table,
                   job_timeout=constants.JOB_TIMEOUT)

  print('Enqueuing global project count')
  upload_q.enqueue(logic_project.update_global_project_count,
                   job_timeout=constants.JOB_TIMEOUT)

if __name__ == '__main__':
  main()
