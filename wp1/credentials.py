"""
Backwards-compatible adapter for the credentials system.

This file reads from the cached Settings instance in wp1.config and
reconstructs the CREDENTIALS[ENV] nested dict that all consumer files
currently expect. Tests install their Settings via conftest.py before this
module is imported, so the snapshot below is built from test configuration
under pytest.

This is a TEMPORARY bridge. As consumers are migrated to use
get_settings().X_Y directly, this file will shrink and eventually be
deleted.
"""

from wp1.config import get_settings
from wp1.environment import Environment

_settings = get_settings()

ENV = _settings.ENV
CONF_LANG = _settings.CONF_LANG

# Build the nested dict that consumers expect, reading all values from the
# settings. Only the active environment section is populated and the others
# are empty.
_active_creds = {
    "WIKIDB": {
        "user": _settings.WIKIDB_USER,
        **(
            {"password": _settings.WIKIDB_PASSWORD} if _settings.WIKIDB_PASSWORD else {}
        ),
        "host": _settings.WIKIDB_HOST,
        "db": _settings.WIKIDB_DB,
        **(
            {"port": _settings.WIKIDB_PORT} if _settings.WIKIDB_PORT is not None else {}
        ),
    },
    "WP10DB": {
        "user": _settings.WP10DB_USER,
        **(
            {"password": _settings.WP10DB_PASSWORD} if _settings.WP10DB_PASSWORD else {}
        ),
        "host": _settings.WP10DB_HOST,
        "port": _settings.WP10DB_PORT,
        "db": _settings.WP10DB_DB,
    },
    "REDIS": {
        "host": _settings.REDIS_HOST,
        "port": _settings.REDIS_PORT,
    },
    "API": {
        **(
            {
                "user": _settings.API_USER,
                "pass": _settings.API_PASSWORD,
            }
            if _settings.API_USER
            else {}
        ),
    },
    "OVERLAY": {
        "update_wait_time_seconds": _settings.OVERLAY_UPDATE_WAIT_TIME,
        "job_elapsed_time_seconds": _settings.OVERLAY_JOB_ELAPSED_TIME,
        "basic_income_total_time_seconds": _settings.OVERLAY_BASIC_INCOME_TOTAL_TIME,
    },
    "MWOAUTH": {
        "consumer_key": _settings.MWOAUTH_CONSUMER_KEY,
        "consumer_secret": _settings.MWOAUTH_CONSUMER_SECRET,
    },
    "SESSION": {
        "secret_key": _settings.SESSION_SECRET_KEY,
    },
    "CLIENT_URL": {
        **({"domains": _settings.CLIENT_DOMAINS} if _settings.CLIENT_DOMAINS else {}),
        **(
            {"homepage": _settings.CLIENT_HOMEPAGE} if _settings.CLIENT_HOMEPAGE else {}
        ),
        **({"s3": _settings.CLIENT_S3_URL} if _settings.CLIENT_S3_URL else {}),
        **({"api": _settings.CLIENT_API_URL} if _settings.CLIENT_API_URL else {}),
        **(
            {"backend": _settings.CLIENT_BACKEND_URL}
            if _settings.CLIENT_BACKEND_URL
            else {}
        ),
        **(
            {"backend_s3": _settings.CLIENT_BACKEND_S3_URL}
            if _settings.CLIENT_BACKEND_S3_URL
            else {}
        ),
    },
    "STORAGE": {
        **({"url": _settings.STORAGE_URL} if _settings.STORAGE_URL is not None else {}),
        "key": _settings.STORAGE_KEY,
        "secret": _settings.STORAGE_SECRET,
        "bucket": _settings.STORAGE_BUCKET,
    },
    "ZIMFARM": {
        "auth_mode": _settings.ZIMFARM_AUTH_MODE,
        "url": _settings.ZIMFARM_URL,
        "s3_url": _settings.ZIMFARM_S3_URL,
        "user": _settings.ZIMFARM_USER,
        "password": _settings.ZIMFARM_PASSWORD,
        "hook_token": _settings.ZIMFARM_HOOK_TOKEN,
        **({"image": _settings.ZIMFARM_IMAGE} if _settings.ZIMFARM_IMAGE else {}),
        **(
            {"definition_version": _settings.ZIMFARM_DEFINITION_VERSION}
            if _settings.ZIMFARM_DEFINITION_VERSION
            else {}
        ),
        **(
            {"cache_url": _settings.ZIMFARM_CACHE_URL}
            if _settings.ZIMFARM_CACHE_URL is not None
            else {}
        ),
        "oauth_issuer": _settings.ZIMFARM_OAUTH_ISSUER,
        "oauth_client_id": _settings.ZIMFARM_OAUTH_CLIENT_ID,
        "oauth_client_secret": _settings.ZIMFARM_OAUTH_CLIENT_SECRET,
        "oauth_audience_id": _settings.ZIMFARM_OAUTH_AUDIENCE_ID,
    },
    "MAILGUN": {
        "url": _settings.MAILGUN_URL,
        "api_key": _settings.MAILGUN_API_KEY,
    },
    "FILE_PATH": {
        "pageviews": _settings.FILE_PATH_PAGEVIEWS,
    },
    "LOGGING": _settings.LOGGING,
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
