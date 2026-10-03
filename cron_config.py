"""Recurring job definitions for RQ's built-in cron scheduler.

Run by the [program:scheduler] supervisord entry as:

    rq cron cron_config.py -u redis://redis

This replaces both system cron in the workers container and rq-scheduler.
Cron strings are evaluated in UTC (RQ uses rq.utils.now(), which is UTC).
"""

from rq import cron

from wp1 import constants, maintenance
from wp1.config import get_settings
from wp1.environment import Environment
from wp1.logic import rating as logic_rating

# Keeps the (slow) all-projects assessment-numbers query warm in the cache.
# The underlying ratings data is rebuilt once per day by the update that
# starts at midnight UTC and takes ~8 hours, so there's no point recomputing
# more than daily. We run at noon UTC, comfortably after that update finishes.
# The cache TTL (see logic.rating.cache_assessment_numbers) is a bit over 24h
# so each day's run refreshes the entry before it can expire.
cron.register(
    logic_rating.update_assessment_cache,
    "assessment-cache",
    cron="0 12 * * *",
    # Without this, the job gets RQ's 180s default timeout, but the query
    # takes minutes in production. Use the repo-wide job timeout.
    job_timeout=constants.JOB_TIMEOUT,
    failure_ttl=constants.JOB_FAILURE_TTL,
)

# The daily maintenance jobs only run in production (in dev there is no data
# pipeline to drive; this matches the old workers image, where dev ran no
# system cron). All three go to the single-worker 'maintenance' queue, which
# serializes them if one runs long.
if get_settings().ENV == Environment.PRODUCTION:
    cron.register(
        maintenance.enqueue_all,
        "maintenance",
        cron="0 0 * * *",
        job_timeout=constants.JOB_TIMEOUT,
        failure_ttl=constants.JOB_FAILURE_TTL,
    )
    cron.register(
        maintenance.update_global_articles,
        "maintenance",
        cron="0 4 * * *",
        job_timeout=maintenance.UPDATE_GLOBAL_JOB_TIMEOUT,
        failure_ttl=constants.JOB_FAILURE_TTL,
    )
    cron.register(
        maintenance.enqueue_global,
        "maintenance",
        cron="0 5 * * *",
        job_timeout=constants.JOB_TIMEOUT,
        failure_ttl=constants.JOB_FAILURE_TTL,
    )
