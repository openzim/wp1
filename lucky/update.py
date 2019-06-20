import argparse
import logging
import re

from lucky.conf import get_conf
import lucky.constants as constants
from lucky.logic import page as logic_page, project as logic_project
from lucky.models.wp10.project import Project
from lucky.wp10_db import conn as wp10db
from lucky.wiki_db import conn as wikidb

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('mwclient').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)
logging.getLogger('requests_oauthlib').setLevel(logging.CRITICAL)
logging.getLogger('oauthlib').setLevel(logging.CRITICAL)

config = get_conf()
ROOT_CATEGORY = config['ROOT_CATEGORY'].encode('utf-8')
CATEGORY_NS = config['CATEGORY_NS'].encode('utf-8')
BY_QUALITY = config['BY_QUALITY'].encode('utf-8')
BY_IMPORTANCE = config['BY_IMPORTANCE'].encode('utf-8')
ARTICLES_LABEL = config['ARTICLES_LABEL'].encode('utf-8')

# %s formatting doesn't work for byes in Python 3.4
RE_REJECT_GENERIC = re.compile(ARTICLES_LABEL + b'_' + BY_QUALITY, re.I)

include_set = None
def get_include_set(args):
  global include_set
  include_set = set()
  if args.includefile is not None:
    with open(args.includefile) as f:
      for line in f:
        include_set.add(line.strip().encode('utf-8'))


exclude_set = None
def get_exclude_set(args):
  global exclude_set
  exclude_set = set()
  if args.excludefile is not None:
    with open(args.excludefile) as f:
      for line in f:
        exclude_set.add(line.strip().encode('utf-8'))


def include_filter(project_iter):
  if len(include_set) == 0:
    # Empty set means include everything
    yield from project_iter
    return

  for project in project_iter:
    if project.p_project in include_set:
      yield project


def exclude_filter(project_iter):
  if len(exclude_set) == 0:
    # Empty set means nothing to exclude
    yield from project_iter
    return

  for project in project_iter:
    if project.p_project not in exclude_set:
      yield project


def project_pages_to_update():
  projects_in_root = logic_page.get_pages_by_category(
    wikidb, ROOT_CATEGORY, constants.CATEGORY_NS_INT)
  for category_page in projects_in_root:
    if (BY_QUALITY not in category_page.page_title or
        BY_IMPORTANCE not in category_page.page_title):
      logger.debug('Skipping %s: it does not have quality/importance in title',
                    category_page.page_title.decode('utf-8'))
      continue

    if RE_REJECT_GENERIC.match(category_page.page_title):
      logger.debug('Skipping %r: it is a generic "articles by quality"',
                    category_page)
      continue

    project = logic_project.get_project_by_name(
      wp10db, category_page.base_title)
    if project is None:
      logger.debug('No project found for %s, creating new one',
                    category_page.base_title)
      project = Project(p_project=category_page.base_title, p_timestamp=None)
    yield project


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--all',
                      help='Attempt to process all projects. This is true by '
                      'default', action='store_true')
  parser.add_argument('--includefile',
                      help='A file with one project per line of projects that' 
                      'should be included and processed')
  parser.add_argument('--excludefile',
                      help='A file with one project per line of projects that' 
                      'should be exclude, ie skipped and not processed. The'
                      'exclusion list takes precedence over the inclusion '
                      'list, so if a project is in both it will be excluded.')
  args = parser.parse_args()

  get_exclude_set(args)
  get_include_set(args)

  if args.all:
    logger.info('Processing all projects, subject to inclusion/exclusion')
    project_iter = exclude_filter(include_filter(project_pages_to_update()))
    for project in project_iter:
      logger.info('Processing %s', project.p_project)
      logic_project.update_project(wikidb, wp10db, project)


if __name__ == '__main__':
  main()
