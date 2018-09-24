import logging
import re
import time

from conf import get_conf
import constants
from logic import page as logic_page
from models.wp10.project import Project
from wp10_db import Session as SessionWP10
from wiki_db import Session as SessionWiki

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

wp10_session = SessionWP10()
wiki_session = SessionWiki()

config = get_conf()
ROOT_CATEGORY = config['ROOT_CATEGORY'].encode('utf-8')
CATEGORY_NS = config['CATEGORY_NS'].encode('utf-8')
BY_QUALITY = config['BY_QUALITY'].encode('utf-8')
ARTICLES_LABEL = config['ARTICLES_LABEL'].encode('utf-8')

# %s formatting doesn't work for byes in Python 3.4
RE_REJECT_GENERIC = re.compile(ARTICLES_LABEL + b'_' + BY_QUALITY, re.I)

GLOBAL_TIMESTAMP = time.strftime('%Y%m%d%H%M%S', time.gmtime())
GLOBAL_TIMESTAMP_WIKI = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

def page_name_to_project():
  return dict((p.project, p) for p in wp10_session.query(Project))

def project_pages_to_update():
  projects_in_root = logic_page.get_pages_by_category(
    wiki_session, ROOT_CATEGORY, constants.CATEGORY_NS_INT)
  for category_page in projects_in_root:
    if BY_QUALITY not in category_page.title:
      logging.debug('Skipping %r: it does not have %s in title',
                    category_page, BY_QUALITY)
      continue

    if RE_REJECT_GENERIC.match(category_page.title):
      logging.debug('Skipping %r: it is a generic "articles by quality"',
                    category_page)
      continue

    yield category_page

