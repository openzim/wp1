import logging

from redis import Redis

from wp1.config import get_settings

logger = logging.getLogger(__name__)


def connect():
    settings = get_settings()
    return Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


def gen_redis_log_key(
    *,
    project: str | bytes,
    namespace: str | bytes,
    action: str | bytes,
    article: str | bytes,
    date: str | bytes | None = None,
) -> str:
    to_str = lambda x: x.decode("utf-8") if isinstance(x, bytes) else x
    key = f"wp1:logs:{to_str(project)}:{to_str(namespace)}:{to_str(action)}:{to_str(article)}"
    if date is not None:
        key += f":{to_str(date)}"
    return key
