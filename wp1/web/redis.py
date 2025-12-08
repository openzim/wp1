import logging

import flask
from redis import Redis
from wp1.credentials import CREDENTIALS, ENV

logger = logging.getLogger(__name__)


def has_redis():
    return hasattr(flask.g, "redis")


def get_redis():
    if not has_redis():
        creds = CREDENTIALS[ENV]["REDIS"]
        setattr(flask.g, "redis", Redis(**creds))
    return getattr(flask.g, "redis")
