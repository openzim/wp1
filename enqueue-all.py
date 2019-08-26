import sys

from redis import Redis
from rq import Queue

from wp1 import constants
from wp1 import logs
from wp1 import tables
from wp1.logic import project as logic_project
from wp1.wiki_db import connect as wiki_connect


def main():
  upload_only = False
  if len(sys.argv) > 1 and sys.argv[1] == '--upload-only':
    upload_only = True

  update_q = Queue('update', connection=Redis(host='redis'))
  upload_q = Queue('upload', connection=Redis(host='redis'))

  if (update_q.count > 0 or upload_q.count > 0):
    print('Queues are not empty. Refusing to add more work.')
    return

  wikidb = wiki_connect()
  for project_name in logic_project.project_names_to_update(wikidb):
    if upload_only:
      print('Enqueuing upload %s' % project_name)
      upload_q.enqueue(tables.upload_project_table,
                       project_name,
                       job_timeout=constants.JOB_TIMEOUT)
    else:
      print('Enqueuing update %s' % project_name)
      update_job = update_q.enqueue(logic_project.update_project_by_name,
                                    project_name,
                                    job_timeout=constants.JOB_TIMEOUT)
      print('Enqueuing upload (dependent) %s' % project_name)
      upload_q.enqueue(tables.upload_project_table,
                       project_name,
                       depends_on=update_job,
                       job_timeout=constants.JOB_TIMEOUT)
      print('Enqueuing log upload (dependent) %s' % project_name)
      upload_q.enqueue(logs.update_log_page_for_project,
                       project_name,
                       depends_on=update_job,
                       job_timeout=constants.JOB_TIMEOUT)


if __name__ == '__main__':
  main()
