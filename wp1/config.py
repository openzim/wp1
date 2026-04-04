"""
Central configuration module for WP1.

Reads configuration from environment variables (loaded from .env files
via python-dotenv). All config values are defined here as flat attributes
on the Config class.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from wp1.environment import Environment

# Load .env from project root (parent of wp1/ directory).
# When running under pytest, load .env.test instead so that WP1_ENV=test
# is set automatically — matching the old credentials.py.e2e behaviour.
# We check both 'pytest' in sys.modules AND the PYTEST_CURRENT_TEST env var
# because config.py may be imported before pytest registers in sys.modules.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_is_testing = "pytest" in sys.modules or "PYTEST_CURRENT_TEST" in os.environ
if _is_testing:
    load_dotenv(_PROJECT_ROOT / ".env.test", override=True)
else:
    load_dotenv(_PROJECT_ROOT / ".env")


def _getenv(key, *, default=None, required=False):

    value = os.environ.get(key)
    if value is None:
        if required:
            raise RuntimeError(
                f"Missing required environment variable: {key}. "
                f"Check your .env file or environment."
            )
        return default
    return value


def _getenv_int(key, *, default=None, required=False):
    value = _getenv(key, default=default, required=required)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        raise RuntimeError(
            f"Invalid integer value for {key}: '{value}'. "
            f"Check your .env file or environment."
        )


def _getenv_list(key, *, default=None, separator=","):
    value = _getenv(key)
    if value is None:
        return default or []
    return [item.strip() for item in value.split(separator) if item.strip()]


def _resolve_env():
    env_str = _getenv("WP1_ENV", default="development")
    mapping = {
        "development": Environment.DEVELOPMENT,
        "production": Environment.PRODUCTION,
        "test": Environment.TEST,
    }
    result = mapping.get(env_str.lower())
    if result is None:
        raise RuntimeError(
            f"Invalid WP1_ENV value: '{env_str}'. "
            f"Must be one of: development, production, test"
        )
    return result


class Config:

    # --- Environment ---
    ENV = _resolve_env()
    CONF_LANG = _getenv("WP1_CONF_LANG", default="en")

    # --- WIKIDB (Wikipedia replica database) ---
    WIKIDB_USER = _getenv("WIKIDB_USER", default="someuser")
    WIKIDB_PASSWORD = _getenv("WIKIDB_PASSWORD", default="somepass")
    WIKIDB_HOST = _getenv(
        "WIKIDB_HOST", default="enwiki.analytics.db.svc.eqiad.wmflabs"
    )
    WIKIDB_DB = _getenv("WIKIDB_DB", default="enwiki_p")
    WIKIDB_PORT = _getenv_int("WIKIDB_PORT")  # None in dev, set in test/CI

    # --- WP10DB (application database) ---
    WP10DB_USER = _getenv("WP10DB_USER", default="root")
    WP10DB_PASSWORD = _getenv("WP10DB_PASSWORD", default="wikipedia")
    WP10DB_HOST = _getenv("WP10DB_HOST", default="localhost")
    WP10DB_PORT = _getenv_int("WP10DB_PORT", default="6300")
    WP10DB_DB = _getenv("WP10DB_DB", default="enwp10_dev")

    # --- Redis ---
    REDIS_HOST = _getenv("REDIS_HOST", default="localhost")
    REDIS_PORT = _getenv_int("REDIS_PORT", default="9736")

    # --- API (Wikipedia bot credentials) ---
    API_USER = _getenv("API_USER")
    API_PASSWORD = _getenv("API_PASSWORD")

    # --- Overlay (development mock queue) ---
    OVERLAY_UPDATE_WAIT_TIME = _getenv_int("OVERLAY_UPDATE_WAIT_TIME", default="40")
    OVERLAY_JOB_ELAPSED_TIME = _getenv_int("OVERLAY_JOB_ELAPSED_TIME", default="10")
    OVERLAY_BASIC_INCOME_TOTAL_TIME = _getenv_int(
        "OVERLAY_BASIC_INCOME_TOTAL_TIME", default="60"
    )

    # --- MWOAUTH (Wikimedia OAuth) ---
    MWOAUTH_CONSUMER_KEY = _getenv("MWOAUTH_CONSUMER_KEY", default="")
    MWOAUTH_CONSUMER_SECRET = _getenv("MWOAUTH_CONSUMER_SECRET", default="")

    # --- Session ---
    SESSION_SECRET_KEY = _getenv("SESSION_SECRET_KEY", default="WP1_secret_key")

    # --- Client URLs ---
    CLIENT_DOMAINS = _getenv_list("CLIENT_DOMAINS", default=["http://localhost:5173"])
    CLIENT_HOMEPAGE = _getenv("CLIENT_HOMEPAGE")
    CLIENT_S3_URL = _getenv("CLIENT_S3_URL")
    CLIENT_API_URL = _getenv("CLIENT_API_URL", default="http://localhost:5000")
    CLIENT_BACKEND_URL = _getenv("CLIENT_BACKEND_URL", default="http://localhost:5000")
    CLIENT_BACKEND_S3_URL = _getenv("CLIENT_BACKEND_S3_URL")

    # --- Storage (S3/MinIO) ---
    STORAGE_URL = _getenv("STORAGE_URL", default="http://localhost:9000/")
    STORAGE_KEY = _getenv("STORAGE_KEY", default="minio_key")
    STORAGE_SECRET = _getenv("STORAGE_SECRET", default="minio_secret")
    STORAGE_BUCKET = _getenv("STORAGE_BUCKET", default="org-kiwix-dev-wp1")

    # --- Zimfarm ---
    ZIMFARM_URL = _getenv("ZIMFARM_URL", default="http://localhost:8003/v2")
    ZIMFARM_S3_URL = _getenv(
        "ZIMFARM_S3_URL", default="https://localhost:9000/org-kiwix-dev-zims"
    )
    ZIMFARM_USER = _getenv("ZIMFARM_USER", default="admin")
    ZIMFARM_PASSWORD = _getenv("ZIMFARM_PASSWORD", default="admin")
    ZIMFARM_HOOK_TOKEN = _getenv("ZIMFARM_HOOK_TOKEN")  # None in dev
    ZIMFARM_IMAGE = _getenv(
        "ZIMFARM_IMAGE", default="ghcr.io/openzim/mwoffliner:1.17.2"
    )
    ZIMFARM_DEFINITION_VERSION = _getenv("ZIMFARM_DEFINITION_VERSION")
    ZIMFARM_CACHE_URL = _getenv("ZIMFARM_CACHE_URL")  # production only

    # --- Mailgun ---
    MAILGUN_URL = _getenv(
        "MAILGUN_URL",
        default="https://api.eu.mailgun.net/v3/mg.wp1.openzim.org/messages",
    )
    MAILGUN_API_KEY = _getenv(
        "MAILGUN_API_KEY", default="INSERT_YOUR_MAILGUN_API_KEY_HERE"
    )

    # --- File paths ---
    FILE_PATH_PAGEVIEWS = _getenv("FILE_PATH_PAGEVIEWS", default="/tmp/pageviews")

    # --- Logging ---
    # Logging directives. Keys are the names of the loggers, values are
    # dictionaries with the logging configuration. The special key '*' sets
    # the default logging configuration. Logging is always done to stdout
    # and is redirected/rotated by the supervisor process.
    # Currently always empty. If per-logger config is needed in the future,
    # consider exposing this via an env var or a logging config file.
    LOGGING = {}
