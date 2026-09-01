"""
Central configuration module for WP1.

The single source of truth for configuration is the frozen Settings class
below. Values are read from environment variables (optionally loaded from a
.env file via python-dotenv). Consumers call get_settings() and read typed
attributes; tests inject configuration with override_settings().

.env.example is GENERATED from this schema. After changing any field, run:

    pipenv run python -m wp1.config

and commit the regenerated file. A test (wp1/config_test.py) fails on drift.
"""

import contextlib
import os
import tempfile
from pathlib import Path

import attrs
from dotenv import load_dotenv

from wp1.environment import Environment

_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Development convenience only. In production and docker the variables come
# from the environment (compose env_file); a missing .env is fine.
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
        return default if default is not None else []
    return [item.strip() for item in value.split(separator) if item.strip()]


def _resolve_env():
    env_str = _getenv("WP1_ENV", default="development")
    mapping = {
        "development": Environment.DEVELOPMENT,
        "production": Environment.PRODUCTION,
    }
    result = mapping.get(env_str.lower())
    if result is None:
        raise RuntimeError(
            f"Invalid WP1_ENV value: '{env_str}'. "
            f"Must be one of: development, production"
        )
    return result


def _field(
    default=None,
    *,
    kind="str",
    env_key=None,
    section=None,
    required_in_production=False,
    help="",
    commented=False,
):
    """A Settings field carrying its env schema in attrs metadata.

    kind: "str" | "int" | "list" | "env" (the Environment enum) | "code"
      ("code" fields are not env-backed and are skipped by both from_env
      and the example generator).
    env_key: environment variable name; defaults to the attribute name.
    section: the "--- Section ---" heading this field is grouped under in
      the generated .env.example.
    commented: emit as a commented-out line in the generated example.
    """
    if isinstance(default, (list, dict)):
        default = attrs.Factory(lambda d=default: type(d)(d))
    return attrs.field(
        default=default,
        metadata={
            "kind": kind,
            "env_key": env_key,
            "section": section,
            "required_in_production": required_in_production,
            "help": help,
            "commented": commented,
        },
    )


@attrs.frozen
class Settings:
    """All WP1 configuration, resolved once and frozen.

    Field declaration order is the order keys appear in the generated
    .env.example.
    """

    # --- Environment ---
    ENV: Environment = _field(
        Environment.DEVELOPMENT,
        kind="env",
        env_key="WP1_ENV",
        section="Environment",
        help=(
            "The environment the app is running in. Controls which behavior "
            "and checks are active.\nValues: development, production"
        ),
    )
    CONF_LANG: str = _field(
        "en",
        env_key="WP1_CONF_LANG",
        section="Environment",
        help=(
            "The directory under conf/ to look for the conf.json file in. So "
            "if this is\n'foo', the file will be loaded as "
            "conf/foo/conf.json. It is okay to check in\nconf.json files, "
            "they don't contain any sensitive information."
        ),
    )

    # --- WIKIDB (Wikipedia replica database) ---
    WIKIDB_USER: str = _field(
        "someuser",
        section="WIKIDB (Wikipedia replica database)",
        required_in_production=True,
        help="EDIT: your Toolforge username.",
    )
    WIKIDB_PASSWORD: str = _field(
        "somepass",
        section="WIKIDB (Wikipedia replica database)",
        required_in_production=True,
        help="EDIT: your Toolforge password.",
    )
    WIKIDB_HOST: str = _field(
        "enwiki.analytics.db.svc.eqiad.wmflabs",
        section="WIKIDB (Wikipedia replica database)",
    )
    WIKIDB_DB: str = _field(
        "enwiki_p",
        section="WIKIDB (Wikipedia replica database)",
    )
    WIKIDB_PORT: int | None = _field(
        None,
        kind="int",
        section="WIKIDB (Wikipedia replica database)",
        commented=True,
        help="Not needed for Option A (SOCKS5 proxy).",
    )

    # --- WP10DB (application database) ---
    WP10DB_USER: str = _field(
        "root",
        section="WP10DB (application database)",
        required_in_production=True,
    )
    WP10DB_PASSWORD: str = _field(
        "wikipedia",
        section="WP10DB (application database)",
        required_in_production=True,
    )
    WP10DB_HOST: str = _field(
        "dev-database",
        section="WP10DB (application database)",
        required_in_production=True,
        help=(
            "Defaults reach the database inside the dev docker network. From "
            "the host\n(e.g. for DB tools), the dev database is published at "
            "localhost:6300."
        ),
    )
    WP10DB_PORT: int | None = _field(
        3306, kind="int", section="WP10DB (application database)"
    )
    WP10DB_DB: str = _field(
        "enwp10_dev",
        section="WP10DB (application database)",
        required_in_production=True,
    )

    # --- Redis ---
    REDIS_HOST: str = _field(
        "redis",
        section="Redis",
        help=(
            "Defaults reach Redis inside the dev docker network. From the "
            "host, it is\npublished at localhost:9736."
        ),
    )
    REDIS_PORT: int | None = _field(6379, kind="int", section="Redis")

    # --- API (Wikipedia bot credentials) ---
    API_USER: str | None = _field(
        None,
        section="API (Wikipedia bot credentials)",
        required_in_production=True,
        commented=True,
    )
    API_PASSWORD: str | None = _field(
        None,
        section="API (Wikipedia bot credentials)",
        required_in_production=True,
        commented=True,
    )

    # --- Overlay (development mock queue) ---
    OVERLAY_UPDATE_WAIT_TIME: int | None = _field(
        40, kind="int", section="Overlay (development mock queue)"
    )
    OVERLAY_JOB_ELAPSED_TIME: int | None = _field(
        10, kind="int", section="Overlay (development mock queue)"
    )
    OVERLAY_BASIC_INCOME_TOTAL_TIME: int | None = _field(
        60, kind="int", section="Overlay (development mock queue)"
    )

    # --- MWOAUTH (Wikimedia OAuth) ---
    MWOAUTH_CONSUMER_KEY: str = _field(
        "",
        section="MWOAUTH (Wikimedia OAuth)",
        required_in_production=True,
    )
    MWOAUTH_CONSUMER_SECRET: str = _field(
        "",
        section="MWOAUTH (Wikimedia OAuth)",
        required_in_production=True,
    )

    # --- Session ---
    SESSION_SECRET_KEY: str = _field(
        "WP1_secret_key",
        section="Session",
        required_in_production=True,
        help="EDIT: set a random secret in production.",
    )

    # --- Client URLs ---
    CLIENT_DOMAINS: list[str] = _field(
        ["http://localhost:5173"],
        kind="list",
        section="Client URLs",
        required_in_production=True,
        help="Comma-separated list of allowed origins for CORS.",
    )
    CLIENT_HOMEPAGE: str | None = _field(
        "http://localhost:5173/#/",
        section="Client URLs",
        required_in_production=True,
    )
    CLIENT_S3_URL: str | None = _field(
        "http://localhost:9000/org-kiwix-dev-wp1",
        section="Client URLs",
        required_in_production=True,
    )
    CLIENT_API_URL: str = _field(
        "http://localhost:5000",
        section="Client URLs",
        required_in_production=True,
    )
    CLIENT_BACKEND_URL: str = _field(
        "http://wp1bot-web-dev:5000",
        section="Client URLs",
        required_in_production=True,
    )

    CLIENT_BACKEND_S3_URL: str | None = _field(
        "http://minio:9000/org-kiwix-dev-wp1",
        section="Client URLs",
        required_in_production=True,
        help=(
            "URL the zimfarm worker uses to reach the selection files over " "S3/MinIO."
        ),
    )

    # --- Storage (S3/MinIO) ---
    STORAGE_URL: str | None = _field(
        "http://minio:9000",
        section="Storage (S3/MinIO)",
        required_in_production=True,
        help=(
            "Defaults reach MinIO inside the dev docker network. From the "
            "host, the\nMinIO API is published at localhost:9000."
        ),
    )
    STORAGE_KEY: str = _field(
        "minio_key",
        section="Storage (S3/MinIO)",
        required_in_production=True,
        help="Username for the storage backend.",
    )
    STORAGE_SECRET: str = _field(
        "minio_secret",
        section="Storage (S3/MinIO)",
        required_in_production=True,
        help="Password for the storage backend.",
    )
    STORAGE_BUCKET: str = _field(
        "org-kiwix-dev-wp1",
        section="Storage (S3/MinIO)",
        required_in_production=True,
    )

    # --- Zimfarm ---
    ZIMFARM_URL: str = _field(
        "http://zimfarm-api/v2",
        section="Zimfarm",
        required_in_production=True,
    )
    ZIMFARM_AUTH_MODE: str = _field(
        "local",
        section="Zimfarm",
        required_in_production=True,
        help="Authentication mode: 'oauth' or 'local'.",
    )
    ZIMFARM_S3_URL: str = _field(
        "https://minio:9000/org-kiwix-dev-zims",
        section="Zimfarm",
        required_in_production=True,
        help="If using minio.",
    )
    ZIMFARM_USER: str = _field("admin", section="Zimfarm")
    ZIMFARM_PASSWORD: str = _field("admin", section="Zimfarm")
    ZIMFARM_HOOK_TOKEN: str | None = _field(
        None,
        section="Zimfarm",
        required_in_production=True,
        commented=True,
        help=(
            "A simple token secret exchanged between the WP1 server and the "
            "zimfarm\nserver, to ensure requests to the webhook endpoint are "
            "valid.\nEDIT: set a strong secret in production."
        ),
    )
    ZIMFARM_IMAGE: str = _field(
        "ghcr.io/openzim/mwoffliner:1.17.2",
        section="Zimfarm",
        help="Update this to the latest version at the time of your deployment.",
    )
    ZIMFARM_DEFINITION_VERSION: str | None = _field(
        "1.17.2",
        section="Zimfarm",
    )
    ZIMFARM_CACHE_URL: str | None = _field(
        None,
        section="Zimfarm",
        commented=True,
        help="Production only (Wasabi cache URL).",
    )
    ZIMFARM_OAUTH_ISSUER: str = _field("https://ory.login.kiwix.org", section="Zimfarm")
    ZIMFARM_OAUTH_CLIENT_ID: str | None = _field(
        None,
        section="Zimfarm",
        commented=True,
        help="Required when ZIMFARM_AUTH_MODE is 'oauth'.",
    )
    ZIMFARM_OAUTH_CLIENT_SECRET: str | None = _field(
        None,
        section="Zimfarm",
        commented=True,
        help="Required when ZIMFARM_AUTH_MODE is 'oauth'.",
    )
    ZIMFARM_OAUTH_AUDIENCE_ID: str | None = _field(
        None,
        section="Zimfarm",
        commented=True,
        help="Required when ZIMFARM_AUTH_MODE is 'oauth'.",
    )

    # --- Mailgun ---
    MAILGUN_URL: str = _field(
        "https://api.eu.mailgun.net/v3/mg.wp1.openzim.org/messages",
        section="Mailgun",
    )
    MAILGUN_API_KEY: str = _field(
        "INSERT_YOUR_MAILGUN_API_KEY_HERE",
        section="Mailgun",
        required_in_production=True,
        help="EDIT this line for production.",
    )

    # --- File paths ---
    FILE_PATH_PAGEVIEWS: str = _field(
        os.path.join(tempfile.gettempdir(), "pageviews"),
        section="File paths",
        help=(
            "Path where the pageviews.bz2 file (~3GB) will be downloaded and "
            "cached.\nThis file is used to calculate article view statistics."
        ),
    )

    # --- Update process ---
    SUPPRESS_RATING_LOGS: int | None = _field(
        0,
        kind="int",
        env_key="WP1_SUPPRESS_RATING_LOGS",
        section="Update process",
        commented=True,
        help=(
            "TEMPORARY escape hatch: when set to 1, project updates emit no\n"
            "assessment-change log entries (the Redis log keys that feed the\n"
            "on-wiki log pages). Intended for a single update cycle when a "
            "fix or\nbackfill would cause a one-time wave of rating churn. "
            "Suppressed logs\nare lost permanently, not deferred; unset "
            "after the cycle completes."
        ),
    )

    # --- Logging ---
    LOGGING_LEVEL: str = _field(
        "INFO",
        section="Logging",
        help="Log level for the root logger (DEBUG, INFO, WARNING, ...).",
    )
    LOGGING_FORMAT: str = _field(
        "%(levelname)s:%(asctime)s:%(name)s:%(message)s",
        section="Logging",
        help="Log line format (Python logging format string).",
    )
    # Per-logger directives, code-only (not env-backed). Keys are logger
    # names, values are dicts with the logging configuration; the special
    # key '*' overrides the root logger config above.
    LOGGING: dict = _field({}, kind="code")

    @classmethod
    def from_env(cls) -> "Settings":
        """Builds a Settings from os.environ, validating required keys."""
        kwargs = {}
        for f in attrs.fields(cls):
            value = _read_field(f)
            if value is not _UNSET:
                kwargs[f.name] = value
        settings = cls(**kwargs)
        _validate(settings)
        return settings


_UNSET = object()


def _read_field(f):
    key = f.metadata["env_key"] or f.name
    kind = f.metadata["kind"]
    if kind == "code":
        return _UNSET
    if kind == "env":
        return _resolve_env()
    if key not in os.environ:
        return _UNSET
    if kind == "int":
        return _getenv_int(key)
    if kind == "list":
        return _getenv_list(key)
    return _getenv(key)


def _validate(settings):
    if settings.ENV == Environment.PRODUCTION:
        # Required keys must be explicitly present (and non-empty) in the
        # environment: development defaults must never silently apply in
        # production.
        missing = [
            key
            for f in attrs.fields(Settings)
            if f.metadata["required_in_production"]
            and not os.environ.get(key := (f.metadata["env_key"] or f.name))
        ]
        if missing:
            raise RuntimeError(
                "Missing required environment variables for production: "
                + ", ".join(missing)
                + ". Check the env file consumed by docker compose."
            )
    if settings.ZIMFARM_AUTH_MODE == "oauth":
        oauth_missing = [
            key
            for key in (
                "ZIMFARM_OAUTH_CLIENT_ID",
                "ZIMFARM_OAUTH_CLIENT_SECRET",
                "ZIMFARM_OAUTH_AUDIENCE_ID",
            )
            if getattr(settings, key) in (None, "")
        ]
        if oauth_missing:
            raise RuntimeError(
                "ZIMFARM_AUTH_MODE=oauth requires: " + ", ".join(oauth_missing)
            )


_settings = None


def get_settings() -> Settings:
    """Returns the process-wide Settings, building it from the environment
    on first use."""
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
    return _settings


def _install_settings(settings) -> None:
    """Replaces the cached settings. Test bootstrap only (see conftest.py)."""
    global _settings
    _settings = settings


@contextlib.contextmanager
def override_settings(settings=None, **changes):
    """Scoped override: swaps the cached Settings for the duration.

    Pass a full Settings instance, or keyword changes that are evolved from
    the currently active one. Restores the previous settings on exit, even
    on exception, so overrides cannot leak between tests.
    """
    global _settings
    if settings is None:
        settings = attrs.evolve(get_settings(), **changes)
    previous = _settings
    _settings = settings
    try:
        yield settings
    finally:
        _settings = previous


# --- .env.example generation ---

_HEADER = """\
# WP1 Configuration
#
# GENERATED FILE - regenerate with: pipenv run python -m wp1.config
# (edit the schema in wp1/config.py, never this file directly).
#
# Copy this file to .env and edit as needed.
#
# Your application database (WP10DB) should work immediately after you run:
#   docker compose -f docker-compose-dev.yml up -d
# in the root directory. The Wiki replica database (WIKIDB) requires actual
# Toolforge credentials (see the WIKIDB section below).
# The test database used by ./scripts/util/run_tests.sh will be available
# when you run:
#   docker compose -f docker-compose-test.yml up -d
"""

# Prose emitted under each section banner in the generated file.
_SECTION_DOCS = {
    "WIKIDB (Wikipedia replica database)": (
        "Database credentials for the Wikipedia replica database hosted on "
        "Wikimedia's\nToolforge infrastructure. This is a read-only replica "
        "of English Wikipedia.\n"
        "\n"
        "There are two ways to access the Wikipedia replica database in "
        "development:\n"
        "\n"
        "Option A - SOCKS5 proxy:\n"
        "  ssh -D 1080 login.toolforge.org\n"
        "(This assumes you have set up your SSH credentials for Toolforge.)\n"
        "Database traffic is tunneled through the proxy so *.eqiad.wmflabs "
        "can resolve.\nUse the values below as-is.\n"
        "\n"
        "Option B - SSH port-forwarding (useful if running inside Docker):\n"
        "  ssh -L 4711:enwiki.analytics.db.svc.eqiad.wmflabs:3306 "
        "login.toolforge.org\n"
        "Then override in your .env:\n"
        "  WIKIDB_HOST=localhost\n"
        "  WIKIDB_PORT=4711"
    ),
    "WP10DB (application database)": (
        "Database credentials for the enwp10 project/application database.\n"
        "For development, use docker-compose-dev.yml to spin up a local "
        "database that\nhas some (potentially out of date) data in it."
    ),
    "Redis": (
        "Credentials for connecting to Redis. In development, this is also "
        "run as a\ndocker-compose service."
    ),
    "API (Wikipedia bot credentials)": (
        "Credentials used by the bot backend to log in to English Wikipedia "
        "and edit\narticles. Not necessary in development (there's no wiki "
        "to edit locally)."
    ),
    "Overlay (development mock queue)": (
        'Options for the "Development overlay" which mocks queue '
        "functionality in the\ndevelopment environment, so you can test "
        "update flows without a real job queue."
    ),
    "MWOAUTH (Wikimedia OAuth)": (
        "Credentials for authentication to Wikimedia through mwoauth. Used "
        'by the\nfrontend/backend to enable the "Login" functionality on '
        "the web app.\n"
        "\n"
        "In DEVELOPMENT mode, OAuth is automatically skipped and a fake "
        "user account\nis created, so these credentials are NOT needed for "
        "local development.\n"
        "\n"
        "For production, register your own app with callback URL:\n"
        "  http://localhost:5000/v1/oauth/complete\n"
        "Register at: "
        "https://meta.wikimedia.org/wiki/Special:OAuthConsumerRegistration/propose"
    ),
    "Session": (
        "Secret key for Flask session encryption. If this ever changes, all "
        "currently\nlogged-in users will be logged out (their session "
        "cookies become invalid).\nTo generate a secure random key for "
        "production:\n"
        '  python3 -c "import os; print(os.urandom(24).hex())"'
    ),
    "Client URLs": (
        "URLs used for redirections, CORS, and internal service " "communication."
    ),
    "Storage (S3/MinIO)": (
        "Configuration for the storage backend for storing selection list "
        "files.\nFor development, you can use the local MinIO instance "
        "that's included in the\ndocker-compose setup (settings below are "
        "pre-configured for this).\n"
        "\n"
        "If you need to use an external service instead, you have two "
        "options:\n"
        "  1. Use the Kiwix S3 backend on Wasabi. Request dev/prod "
        "credentials from the team.\n"
        "     See https://github.com/openzim/zimfarm/wiki/S3-Cache-Policy "
        "for how.\n"
        "  2. Use another S3-compatible storage service (AWS S3, etc.).\n"
        "In either external case, edit the settings below accordingly."
    ),
    "Zimfarm": (
        "Server URL and credentials for the Zim Farm that creates ZIM files "
        "from\nmaterialized selections."
    ),
    "Mailgun": (
        "Credentials for the Mailgun service, used to send email "
        "notifications to users\nwhen their requested/scheduled ZIM files "
        "are ready. Not required for development."
    ),
    "File paths": "",
    "Update process": "",
    "Logging": (
        "Configuration for the root logger. Logging is always done to "
        "stdout and is\nredirected/rotated by the supervisor process."
    ),
}


def _example_value(f):
    default = f.default
    if isinstance(default, attrs.Factory):
        default = default.factory()
    if f.metadata["kind"] == "env":
        return "development"
    if f.metadata["kind"] == "list":
        return ",".join(default)
    if default is None:
        return ""
    return str(default)


def _comment_block(text):
    return [f"# {line}" if line else "#" for line in text.split("\n")]


def generate_example() -> str:
    """Returns the full text of .env.example, generated from the schema."""
    lines = [_HEADER]
    current_section = None
    for f in attrs.fields(Settings):
        if f.metadata["kind"] == "code":
            continue
        section = f.metadata["section"]
        if section != current_section:
            current_section = section
            lines.append("")
            lines.append(f"# --- {section} ---")
            doc = _SECTION_DOCS.get(section, "")
            if doc:
                lines.extend(_comment_block(doc))
            lines.append("")
        if f.metadata["help"]:
            lines.extend(_comment_block(f.metadata["help"]))
        if f.metadata["required_in_production"]:
            lines.append("# Required in production.")
        key = f.metadata["env_key"] or f.name
        prefix = "# " if f.metadata["commented"] else ""
        lines.append(f"{prefix}{key}={_example_value(f)}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    (_PROJECT_ROOT / ".env.example").write_text(generate_example())
    print("Wrote .env.example")
