"""Recurring maintenance jobs for the workers container.

These replace the shell scripts in cron/ that were driven by system cron. They
are registered as recurring jobs in cron_config.py (run by `rq cron`) and
executed by the single-worker 'maintenance' queue, which serializes them.
"""

import logging
import subprocess
import time

from redis import Redis
from rq import Queue
from rq.command import send_stop_job_command
from rq.registry import StartedJobRegistry
from rq.suspension import resume, suspend

import wp1.logic.project as logic_project
from wp1 import constants, queues, tables
from wp1.credentials import ENV
from wp1.environment import Environment
from wp1.redis_db import connect as redis_connect
from wp1.wiki_db import connect as wiki_connect
from wp1.wp10_db import connect as wp10_connect

logger = logging.getLogger(__name__)

# How long update_global_articles waits for the stopped in-flight update jobs
# to actually die after being sent the stop command, before giving up (and
# trying again tomorrow).
DRAIN_TIMEOUT_SECONDS = 60 * 10
DRAIN_POLL_SECONDS = 5

# Backstop TTL on the Redis suspension key: if the job dies without reaching
# resume() (OOM-kill, container restart), workers un-suspend themselves after
# this long instead of staying paused forever.
SUSPEND_TTL_SECONDS = 60 * 60 * 8

# Must cover the global articles rebuild itself.
UPDATE_GLOBAL_JOB_TIMEOUT = 60 * 60 * 6

# The queues whose in-flight jobs write project ratings data and therefore
# must be drained before the global articles rebuild.
_UPDATE_QUEUE_NAMES = ("update", "manual-update")


def enqueue_all():
    """Nightly (midnight UTC): enqueue update + upload jobs for all projects."""
    _restart_upload_workers()
    redis = redis_connect()
    wp10db = wp10_connect()
    queues.enqueue_all_projects(redis, wp10db)


def update_global_articles():
    """Daily (04:00 UTC): rebuild the global articles table.

    The rebuild needs the update workers quiet so that project updates aren't
    writing ratings data while it runs, and it supersedes any per-project
    update jobs that are still in flight — so those are stopped rather than
    waited on (equivalent to the old cron script's supervisorctl stop, which
    killed them after 10 seconds). Suspends dequeueing on all RQ workers,
    stops in-flight update jobs, rebuilds, and resumes.
    """
    redis = redis_connect()
    suspend(redis, ttl=SUSPEND_TTL_SECONDS)
    try:
        _stop_inflight_update_jobs(redis)
        _wait_for_update_jobs_to_drain(redis)
        rebuild_global_articles()
    finally:
        resume(redis)


def enqueue_global():
    """Daily (05:00 UTC): enqueue the global table upload and project count."""
    redis = redis_connect()
    upload_q = Queue("upload", connection=redis)

    if ENV == Environment.PRODUCTION:
        logger.info("Enqueuing global table upload")
        upload_q.enqueue(tables.upload_global_table, job_timeout=constants.JOB_TIMEOUT)

    logger.info("Enqueuing global project count")
    upload_q.enqueue(
        logic_project.update_global_project_count, job_timeout=constants.JOB_TIMEOUT
    )


def rebuild_global_articles():
    """Update the global articles table for every project, with no locking.

    Callers are responsible for quiescing the update workers first if needed
    (see update_global_articles).
    """
    wikidb = wiki_connect()
    wp10db = wp10_connect()

    for project_name in logic_project.project_names_to_update(wikidb):
        logic_project.update_global_articles_for_project_name(wp10db, project_name)


def _stop_inflight_update_jobs(redis: Redis):
    """Tell the workers to kill any currently-executing update jobs."""
    for queue_name in _UPDATE_QUEUE_NAMES:
        registry = StartedJobRegistry(queue=Queue(queue_name, connection=redis))
        for job_id in registry.get_job_ids():
            try:
                send_stop_job_command(redis, job_id)
                logger.info("Stopped in-flight update job %s", job_id)
            except Exception as e:
                # Typically the job finished between listing and stopping.
                logger.info("Could not stop update job %s: %s", job_id, e)


def _wait_for_update_jobs_to_drain(redis: Redis):
    deadline = time.monotonic() + DRAIN_TIMEOUT_SECONDS
    while True:
        busy = 0
        for queue_name in _UPDATE_QUEUE_NAMES:
            registry = StartedJobRegistry(queue=Queue(queue_name, connection=redis))
            busy += registry.count
        if busy == 0:
            return
        if time.monotonic() >= deadline:
            raise TimeoutError(
                "Gave up waiting for %d in-flight update job(s) to finish" % busy
            )
        logger.info("Waiting for %d in-flight update job(s) to finish", busy)
        time.sleep(DRAIN_POLL_SECONDS)


def _restart_upload_workers():
    """Bounce the upload workers, as cron/enqueue-all.sh did before the nightly
    enqueue. Best-effort: everything runs in the same container as supervisord,
    but if the restart fails the enqueue should still happen.
    """
    try:
        subprocess.run(
            ["supervisorctl", "-c", "supervisord.conf", "restart", "wp1-upload:*"],
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (OSError, subprocess.SubprocessError) as e:
        logger.warning("Could not restart upload workers: %s", e)
