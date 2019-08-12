import sys

from redis import Redis
from rq import Queue

import lucky.logic.project as logic_project
from lucky import tables

def main():
  update_q = Queue('update', connection=Redis(host='redis'))
  upload_q = Queue('upload', connection=Redis(host='redis'))

  project_names = sys.argv[1:]
  print(project_names)

  for project_name in project_names:
    print('Enqueuing update %s' % project_name)
    update_job = update_q.enqueue(
      logic_project.update_project_by_name, project_name)
    print('Enqueuing upload (dependent) %s' % project_name)
    upload_q.enqueue(
      tables.upload_project_table, project_name, depends_on=update_job)


if __name__ == '__main__':
  main()
