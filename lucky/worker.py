import sys

from redis import Redis
from rq import Connection, Worker

# Preload API so login is only done once
import lucky.api

conn = Redis(host='redis')
with Connection(conn):
    qs = sys.argv[1:] or ['default']

    w = Worker(qs)
    w.work()
