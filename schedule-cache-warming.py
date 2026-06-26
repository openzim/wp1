import logging

from wp1 import app_logging, queues
from wp1.redis_db import connect as redis_connect

logger = logging.getLogger(__name__)


def main():
    app_logging.configure_logging()

    redis = redis_connect()
    queues.schedule_assessment_cache_warming(redis)
    logger.info("Registered recurring assessment-cache warming schedule")


if __name__ == "__main__":
    main()
