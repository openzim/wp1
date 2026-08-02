"""Recurring maintenance jobs for the workers container.

These replace the shell scripts in cron/ that were driven by system cron. They
are registered as recurring jobs in cron_config.py (run by `rq cron`) and
executed by the single-worker 'maintenance' queue, which serializes them.
"""

import logging
import subprocess

from redis import Redis
from rq import Queue
from rq.command import send_stop_job_command
from rq.registry import StartedJobRegistry

import wp1.logic.project as logic_project
from wp1 import constants, queues, tables
from wp1.credentials import ENV
from wp1.environment import Environment
from wp1.redis_db import connect as redis_connect
from wp1.wiki_db import connect as wiki_connect
from wp1.wp10_db import connect as wp10_connect

logger = logging.getLogger(__name__)

# Must cover the global articles rebuild itself.
UPDATE_GLOBAL_JOB_TIMEOUT = 60 * 60 * 6

# Everything in the workers container runs from this supervisord config,
# including the maintenance-queue worker these jobs execute on.
SUPERVISORD_CONF = "/usr/src/app/supervisord.conf"

# The supervisord group of workers for the 'update' queue. The maintenance
# worker must never be part of this group, or update_global_articles would
# kill its own worker.
UPDATE_WORKER_GROUP = "wp1-update:*"


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
    update jobs that are still in flight. Those jobs are sent a stop command
    (so they die cleanly instead of via supervisord's 10s SIGKILL) and then
    the update worker processes are stopped for the duration of the rebuild.
    Only the 'update' workers are touched: all other queues (materializer,
    manual-update, zimfile-*, upload) keep serving users throughout.
    """
    redis = redis_connect()
    _stop_inflight_update_jobs(redis)
    # If the workers can't be stopped, this raises and the rebuild is
    # aborted: rebuilding while update jobs run risks inconsistent data.
    _supervisorctl("stop", UPDATE_WORKER_GROUP)
    try:
        rebuild_global_articles()
    finally:
        _supervisorctl("start", UPDATE_WORKER_GROUP)


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
    registry = StartedJobRegistry(queue=Queue("update", connection=redis))
    for job_id in registry.get_job_ids():
        try:
            send_stop_job_command(redis, job_id)
            logger.info("Sent stop command to in-flight update job %s", job_id)
        except Exception as e:
            # Typically the job finished between listing and stopping.
            logger.info("Could not stop update job %s: %s", job_id, e)


def _restart_upload_workers():
    """Bounce the upload workers, as cron/enqueue-all.sh did before the nightly
    enqueue. Best-effort: if the restart fails the enqueue should still happen.
    """
    try:
        _supervisorctl("restart", "wp1-upload:*")
    except (OSError, subprocess.SubprocessError) as e:
        logger.warning("Could not restart upload workers: %s", e)


def _supervisorctl(*args: str):
    subprocess.run(
        ["supervisorctl", "-c", SUPERVISORD_CONF, *args],
        check=True,
        capture_output=True,
        text=True,
        # Stopping the update worker group can take up to ~10s per busy
        # worker (supervisord's TERM-then-kill window).
        timeout=300,
    )
