import logging
import re

import lucky.constants as constants
from lucky.logic import page as logic_page, project as logic_project
from lucky.models.wp10.project import Project
from lucky.wiki_db import conn as wikidb
from lucky.wp10_db import conn as wp10db

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logging.getLogger('mwclient').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)
logging.getLogger('requests_oauthlib').setLevel(logging.CRITICAL)
logging.getLogger('oauthlib').setLevel(logging.CRITICAL)

try:
  logic_project.update_project(wikidb, wp10db, Project(p_project=b'Catholicism', p_timestamp=None))
finally:
  wikidb.close()
  wp10db.close()
