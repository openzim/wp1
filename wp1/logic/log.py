import datetime

import attr
from redis import Redis
from wp1.redis_db import gen_redis_log_key
from wp1.models.wp10.log import Log

# Redis does not allow None types. However if a log to be stored has a None
# we convert it to this value while storing on Redis and back to None
# when converting from Redis to python object
REDIS_NULL = b"__redis__none__"


def insert_or_update(redis: Redis, log: Log):
  log_key = gen_redis_log_key(project=log.l_project,
                              namespace=log.l_namespace,
                              action=log.l_action,
                              article=log.l_article)
  with redis.pipeline() as pipe:
    mapping = {
        k: REDIS_NULL if v is None else v for k, v in attr.asdict(log).items()
    }
    pipe.hset(log_key, mapping=mapping)
    pipe.expire(log_key, datetime.timedelta(days=7))
    pipe.execute()


def get_logs(
    redis: Redis,
    *,
    project: str | bytes = "*",
    namespace: str | bytes = "*",
    action: str | bytes = "*",
    article: str | bytes = "*",
    start_dt: datetime.datetime | None = None,
) -> list[Log]:
  """Retrieve logs from Redis matching the given filters."""
  key = gen_redis_log_key(project=project,
                          namespace=namespace,
                          action=action,
                          article=article)
  logs: list[Log] = []
  for log_key in redis.scan_iter(match=key, _type="HASH"):
    data = redis.hgetall(log_key)
    # convert the data according to the field types of the Log object
    log_dict = {
        k.decode("utf-8"): v if v != REDIS_NULL else None
        for k, v in data.items()
    }
    if log_dict["l_namespace"] is not None:
      log_dict["l_namespace"] = int(log_dict["l_namespace"])

    log = Log(**log_dict)
    # skip logs that are not newer than start_dt
    if start_dt is not None and log.timestamp_dt < start_dt:
      continue
    logs.append(log)

  return logs
