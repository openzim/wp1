import logging
import sys

from wp1 import constants
from wp1 import tables
from wp1.conf import get_conf
from wp1.logic import page as logic_page, project as logic_project
from wp1.wiki_db import connect as wiki_connect
from wp1.wp10_db import connect as wp10_connect


def main():
  wikidb = wiki_connect()
  wp10db = wp10_connect()

  logging.basicConfig(level=logging.INFO)

  for project_name in logic_project.project_names_to_update(wikidb):
    logic_project.update_global_articles_for_project_name(wp10db, project_name)


if __name__ == '__main__':
  main()
