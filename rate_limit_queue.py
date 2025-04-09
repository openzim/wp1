import time

from rq import Queue


class RateLimitQueue(Queue):
  last_dequeue_time = None
  wait_time_secs = 1

  @classmethod
  def dequeue_any(cls, *args, **kwargs):
    job, queue = super().dequeue_any(*args, **kwargs)
    if job and queue:
      cur_time = int(time.time())
      time_diff = 0
      if cls.last_dequeue_time is not None:
        time_diff = cur_time - cls.last_dequeue_time
      if time_diff <= cls.wait_time_secs:
        time.sleep(cls.wait_time_secs - time_diff)
      cls.last_dequeue_time = int(time.time())
      return job, queue
    return job, queue
