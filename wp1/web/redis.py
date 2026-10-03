import logging

import flask
from redis import Redis
from wp1.config import get_settings

logger = logging.getLogger(__name__)


def has_redis():
    return hasattr(flask.g, "redis")


def get_redis():
    if not has_redis():
        settings = get_settings()
        setattr(
            flask.g, "redis", Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
        )
    return getattr(flask.g, "redis")
