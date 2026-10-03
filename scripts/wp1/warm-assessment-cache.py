import logging
import sys
from pathlib import Path

# Runs as `python scripts/wp1/warm-assessment-cache.py`; put the repo root on
# sys.path so the `wp1` package resolves regardless of cwd.
# The config defaults point at in-docker hostnames, so in development run
# this inside the stack:
#   docker compose -f docker-compose-dev.yml exec dev-web \
#     python scripts/wp1/warm-assessment-cache.py
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from wp1 import app_logging, queues
from wp1.redis_db import connect as redis_connect

logger = logging.getLogger(__name__)


def main():
    app_logging.configure_logging()

    # Seed the cache immediately so a fresh deploy / Redis restart doesn't
    # leave the slow query to run inline on web requests until the next
    # scheduled (noon UTC, see cron_config.py) run.
    redis = redis_connect()
    queues.enqueue_assessment_cache_warming(redis)
    logger.info("Enqueued immediate assessment-cache warming job")


if __name__ == "__main__":
    main()
