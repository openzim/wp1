import sys

from redis import Redis
from rq import Connection, Queue
from rq_retry import RetryWorker

# Preload API so login is only done once
import wp1.api

conn = Redis(host='redis')
with Connection(conn):
    qs = sys.argv[1:] or ['default']

    # Retry failed jobs after 30 seconds, then 180 seconds.
    w = RetryWorker(qs, retry_config={'delays': [30,180], 'max_tries': 5})
    # Workaround for apparent bug in RetryWorker.
    w.failed_queue = Queue('failed', connection=conn)
    w.work()
