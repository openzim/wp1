import re
import sys

from redis import Redis
from rq import Queue

from wp1 import constants
from wp1 import tables
from wp1.conf import get_conf
from wp1.logic import page as logic_page, project as logic_project
from wp1.wiki_db import connect as wiki_connect

config = get_conf()
ROOT_CATEGORY = config['ROOT_CATEGORY'].encode('utf-8')
CATEGORY_NS = config['CATEGORY_NS'].encode('utf-8')
BY_QUALITY = config['BY_QUALITY'].encode('utf-8')
BY_IMPORTANCE = config['BY_IMPORTANCE'].encode('utf-8')
ARTICLES_LABEL = config['ARTICLES_LABEL'].encode('utf-8')

RE_REJECT_GENERIC = re.compile(ARTICLES_LABEL + b'_' + BY_QUALITY, re.I)


def project_names_to_update(wikidb):
  projects_in_root = logic_page.get_pages_by_category(
    wikidb, ROOT_CATEGORY, constants.CATEGORY_NS_INT)
  # List instead of iterate because the query will be reused in the processing
  # steps and if we don't exhaust it now, it will get truncated.
  for category_page in list(projects_in_root):
    if BY_QUALITY not in category_page.page_title:
      print('Skipping %s -- it does not have quality in title' %
                    category_page.page_title.decode('utf-8'))
      continue

    if RE_REJECT_GENERIC.match(category_page.page_title):
      print('Skipping %r -- it is a generic "articles by quality"' %
                    category_page)
      continue

    yield category_page.base_title


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
  for project_name in project_names_to_update(wikidb):
    if upload_only:
      print('Enqueuing upload (dependent) %s' % project_name)
      upload_q.enqueue(
        tables.upload_project_table, project_name,
        job_timeout=constants.JOB_TIMEOUT)
    else:
      print('Enqueuing update %s' % project_name)
      update_job = update_q.enqueue(
        logic_project.update_project_by_name, project_name,
        job_timeout=constants.JOB_TIMEOUT)
      print('Enqueuing upload (dependent) %s' % project_name)
      upload_q.enqueue(
        tables.upload_project_table, project_name,
        depends_on=update_job, job_timeout=constants.JOB_TIMEOUT)

if __name__ == '__main__':
  main()
