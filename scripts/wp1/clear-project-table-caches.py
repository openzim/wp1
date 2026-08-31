import logging
import sys
from pathlib import Path

# Runs as `python scripts/wp1/clear-project-table-caches.py`; put the repo
# root on sys.path so the `wp1` package resolves regardless of cwd.
# The config defaults point at in-docker hostnames, so in development run
# this inside the stack:
#   docker compose -f docker-compose-dev.yml exec dev-web \
#     python scripts/wp1/clear-project-table-caches.py
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from wp1 import app_logging
from wp1.logic import project as logic_project
from wp1.redis_db import connect as redis_connect
from wp1.wp10_db import connect as wp10_connect

logger = logging.getLogger(__name__)


def main():
    app_logging.configure_logging()

    wp10db = wp10_connect()
    redis = redis_connect()

    for project in logic_project.list_all_projects(wp10db):
        logger.info(f"Clearing cache for project {project.p_project.decode('utf-8')}")
        redis.delete(project.p_project)


if __name__ == "__main__":
    main()
