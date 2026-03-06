"""

Backwards-compatible adapter for the credentials system.

This file reads from wp1.config (which reads from .env files and environment
variables) and reconstructs the CREDENTIALS[ENV] nested dict that all
consumer files currently expect.

This is a TEMPORARY bridge. As consumers are migrated to use Config.X_Y
directly, this file will shrink and eventually be deleted.

"""

from wp1.config import Config
from wp1.environment import Environment

ENV = Config.ENV
CONF_LANG = Config.CONF_LANG

# Build the nested dict that consumers expect, reading all values from Config.
# Only the active environment section is populated and the others are empty.
_active_creds = {
    "WIKIDB": {
        "user": Config.WIKIDB_USER,
        **({"password": Config.WIKIDB_PASSWORD} if Config.WIKIDB_PASSWORD else {}),
        "host": Config.WIKIDB_HOST,
        "db": Config.WIKIDB_DB,
        **({"port": Config.WIKIDB_PORT} if Config.WIKIDB_PORT is not None else {}),
    },
    "WP10DB": {
        "user": Config.WP10DB_USER,
        **({"password": Config.WP10DB_PASSWORD} if Config.WP10DB_PASSWORD else {}),
        "host": Config.WP10DB_HOST,
        "port": Config.WP10DB_PORT,
        "db": Config.WP10DB_DB,
    },
    "REDIS": {
        "host": Config.REDIS_HOST,
        "port": Config.REDIS_PORT,
    },
    "API": {
        **(
            {
                "user": Config.API_USER,
                "pass": Config.API_PASSWORD,
            }
            if Config.API_USER
            else {}
        ),
    },
    "OVERLAY": {
        "update_wait_time_seconds": Config.OVERLAY_UPDATE_WAIT_TIME,
        "job_elapsed_time_seconds": Config.OVERLAY_JOB_ELAPSED_TIME,
        "basic_income_total_time_seconds": Config.OVERLAY_BASIC_INCOME_TOTAL_TIME,
    },
    "MWOAUTH": {
        "consumer_key": Config.MWOAUTH_CONSUMER_KEY,
        "consumer_secret": Config.MWOAUTH_CONSUMER_SECRET,
    },
    "SESSION": {
        "secret_key": Config.SESSION_SECRET_KEY,
    },
    "CLIENT_URL": {
        **({"domains": Config.CLIENT_DOMAINS} if Config.CLIENT_DOMAINS else {}),
        **({"homepage": Config.CLIENT_HOMEPAGE} if Config.CLIENT_HOMEPAGE else {}),
        **({"s3": Config.CLIENT_S3_URL} if Config.CLIENT_S3_URL else {}),
        **({"api": Config.CLIENT_API_URL} if Config.CLIENT_API_URL else {}),
        **({"backend": Config.CLIENT_BACKEND_URL} if Config.CLIENT_BACKEND_URL else {}),
        **(
            {"backend_s3": Config.CLIENT_BACKEND_S3_URL}
            if Config.CLIENT_BACKEND_S3_URL
            else {}
        ),
    },
    "STORAGE": {
        **({"url": Config.STORAGE_URL} if Config.STORAGE_URL is not None else {}),
        "key": Config.STORAGE_KEY,
        "secret": Config.STORAGE_SECRET,
        "bucket": Config.STORAGE_BUCKET,
    },
    "ZIMFARM": {
        "url": Config.ZIMFARM_URL,
        "s3_url": Config.ZIMFARM_S3_URL,
        "user": Config.ZIMFARM_USER,
        "password": Config.ZIMFARM_PASSWORD,
        "hook_token": Config.ZIMFARM_HOOK_TOKEN,
        **({"image": Config.ZIMFARM_IMAGE} if Config.ZIMFARM_IMAGE else {}),
        **(
            {"definition_version": Config.ZIMFARM_DEFINITION_VERSION}
            if Config.ZIMFARM_DEFINITION_VERSION
            else {}
        ),
        **(
            {"cache_url": Config.ZIMFARM_CACHE_URL}
            if Config.ZIMFARM_CACHE_URL is not None
            else {}
        ),
    },
    "MAILGUN": {
        "url": Config.MAILGUN_URL,
        "api_key": Config.MAILGUN_API_KEY,
    },
    "FILE_PATH": {
        "pageviews": Config.FILE_PATH_PAGEVIEWS,
    },
    "LOGGING": Config.LOGGING,
}

# The CREDENTIALS dict keyed by environment
# DEVELOPMENT and TEST are always populated with active config values so that
# code which patches ENV (e.g test_socks_proxy) still works.
# PRODUCTION is only populated when WP1_ENV=production
CREDENTIALS = {
    Environment.DEVELOPMENT: _active_creds,
    Environment.TEST: _active_creds,
    Environment.PRODUCTION: (_active_creds if ENV == Environment.PRODUCTION else {}),
}
