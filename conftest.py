"""Pytest bootstrap: install test configuration, in code.

This runs before any wp1 module is imported, so every get_settings() call in
the test process sees these values. There is no .env.test and no WP1_ENV=test:
test configuration lives here, in typed Python, and per-test tweaks go
through wp1.config.override_settings(). Because the settings are installed
before anything reads the environment, values from a developer's .env
(auto-loaded by pipenv) can never leak into a test run.

The values mirror docker-compose-test.yml (MySQL on localhost:6600, Redis on
localhost:9777) - CI maps its services to the same ports.
"""

from wp1.config import Settings, _install_settings
from wp1.environment import Environment

TEST_SETTINGS = Settings(
    ENV=Environment.TEST,
    CONF_LANG="en",
    WIKIDB_USER="root",
    WIKIDB_PASSWORD="",
    WIKIDB_HOST="localhost",
    WIKIDB_PORT=6600,
    WIKIDB_DB="enwikip_test",
    WP10DB_USER="root",
    WP10DB_PASSWORD="",
    WP10DB_HOST="localhost",
    WP10DB_PORT=6600,
    WP10DB_DB="enwp10_test",
    REDIS_HOST="localhost",
    REDIS_PORT=9777,
    API_USER="",
    API_PASSWORD="",
    MWOAUTH_CONSUMER_KEY="",
    MWOAUTH_CONSUMER_SECRET="",
    SESSION_SECRET_KEY="WP1",
    CLIENT_DOMAINS=[],
    CLIENT_HOMEPAGE=None,
    CLIENT_S3_URL=None,
    CLIENT_API_URL="http://test.server.fake",
    CLIENT_BACKEND_URL="http://test.server.fake",
    CLIENT_BACKEND_S3_URL=None,
    STORAGE_URL="",
    STORAGE_KEY="test_key",
    STORAGE_SECRET="test_secret",
    STORAGE_BUCKET="org-kiwix-dev-wp1",
    ZIMFARM_AUTH_MODE="local",
    ZIMFARM_URL="https://fake.farm/v2",
    ZIMFARM_S3_URL="https://fake.wasabisys.com/org-kiwix-zimit",
    ZIMFARM_USER="farmuser",
    ZIMFARM_PASSWORD="farmpass",
    ZIMFARM_HOOK_TOKEN="hook-token-abc",
    ZIMFARM_IMAGE="",
    ZIMFARM_DEFINITION_VERSION="",
    ZIMFARM_CACHE_URL="",
    # FILE_PATH_PAGEVIEWS is not set here: the schema default (a
    # "pageviews" directory under the system temp dir) is already the
    # right value for tests.
)

_install_settings(TEST_SETTINGS)
