import unittest
from pathlib import Path
from unittest.mock import patch

import attrs

import wp1.config
from wp1.config import (
    Settings,
    _getenv,
    _getenv_int,
    _getenv_list,
    _resolve_env,
    generate_example,
    get_settings,
    override_settings,
)
from wp1.environment import Environment


class GetenvTest(unittest.TestCase):

    @patch.dict("os.environ", {"TEST_KEY": "hello"}, clear=False)
    def test_returns_value_when_set(self):
        self.assertEqual("hello", _getenv("TEST_KEY"))

    @patch.dict("os.environ", {}, clear=False)
    def test_returns_default_when_not_set(self):
        self.assertEqual("fallback", _getenv("MISSING_KEY", default="fallback"))

    @patch.dict("os.environ", {}, clear=False)
    def test_returns_none_when_not_set_and_no_default(self):
        self.assertIsNone(_getenv("MISSING_KEY"))

    @patch.dict("os.environ", {}, clear=False)
    def test_raises_when_required_and_missing(self):
        with self.assertRaises(RuntimeError) as ctx:
            _getenv("MISSING_KEY", required=True)
        self.assertIn("MISSING_KEY", str(ctx.exception))


class GetenvIntTest(unittest.TestCase):

    @patch.dict("os.environ", {"INT_KEY": "42"}, clear=False)
    def test_returns_int_value(self):
        self.assertEqual(42, _getenv_int("INT_KEY"))

    @patch.dict("os.environ", {}, clear=False)
    def test_returns_none_when_not_set(self):
        self.assertIsNone(_getenv_int("MISSING_KEY"))

    @patch.dict("os.environ", {}, clear=False)
    def test_returns_default_as_int(self):
        self.assertEqual(99, _getenv_int("MISSING_KEY", default="99"))

    @patch.dict("os.environ", {"INT_KEY": "not_a_number"}, clear=False)
    def test_raises_on_invalid_int(self):
        with self.assertRaises(RuntimeError) as ctx:
            _getenv_int("INT_KEY")
        self.assertIn("INT_KEY", str(ctx.exception))
        self.assertIn("not_a_number", str(ctx.exception))

    @patch.dict("os.environ", {"INT_KEY": ""}, clear=False)
    def test_raises_on_empty_string(self):
        with self.assertRaises(RuntimeError) as ctx:
            _getenv_int("INT_KEY")
        self.assertIn("INT_KEY", str(ctx.exception))


class GetenvListTest(unittest.TestCase):

    @patch.dict("os.environ", {"LIST_KEY": "a,b,c"}, clear=False)
    def test_parses_comma_separated(self):
        self.assertEqual(["a", "b", "c"], _getenv_list("LIST_KEY"))

    @patch.dict("os.environ", {"LIST_KEY": " a , b , c "}, clear=False)
    def test_strips_whitespace(self):
        self.assertEqual(["a", "b", "c"], _getenv_list("LIST_KEY"))

    @patch.dict("os.environ", {"LIST_KEY": "single"}, clear=False)
    def test_single_item(self):
        self.assertEqual(["single"], _getenv_list("LIST_KEY"))

    @patch.dict("os.environ", {"LIST_KEY": ""}, clear=False)
    def test_empty_string_returns_empty_list(self):
        self.assertEqual([], _getenv_list("LIST_KEY"))

    @patch.dict("os.environ", {}, clear=False)
    def test_returns_default_when_not_set(self):
        self.assertEqual(["default"], _getenv_list("MISSING_KEY", default=["default"]))

    @patch.dict("os.environ", {}, clear=False)
    def test_returns_empty_list_when_not_set_and_no_default(self):
        self.assertEqual([], _getenv_list("MISSING_KEY"))

    @patch.dict("os.environ", {"LIST_KEY": "a,,b,,c"}, clear=False)
    def test_skips_empty_entries(self):
        self.assertEqual(["a", "b", "c"], _getenv_list("LIST_KEY"))


class ResolveEnvTest(unittest.TestCase):

    @patch.dict("os.environ", {"WP1_ENV": "development"}, clear=False)
    def test_development(self):
        self.assertEqual(Environment.DEVELOPMENT, _resolve_env())

    @patch.dict("os.environ", {"WP1_ENV": "production"}, clear=False)
    def test_production(self):
        self.assertEqual(Environment.PRODUCTION, _resolve_env())

    @patch.dict("os.environ", {"WP1_ENV": "test"}, clear=False)
    def test_raises_on_test_value(self):
        # Test configuration lives in code (conftest.py); WP1_ENV=test is
        # no longer a valid environment name.
        with self.assertRaises(RuntimeError):
            _resolve_env()

    @patch.dict("os.environ", {"WP1_ENV": "DEVELOPMENT"}, clear=False)
    def test_case_insensitive(self):
        self.assertEqual(Environment.DEVELOPMENT, _resolve_env())

    @patch.dict("os.environ", {"WP1_ENV": "staging"}, clear=False)
    def test_raises_on_invalid_value(self):
        with self.assertRaises(RuntimeError) as ctx:
            _resolve_env()
        self.assertIn("staging", str(ctx.exception))


class SettingsFromEnvTest(unittest.TestCase):

    @patch.dict(
        "os.environ",
        {"WP10DB_PORT": "1234", "CLIENT_DOMAINS": "http://a,http://b"},
        clear=False,
    )
    def test_reads_typed_values(self):
        settings = Settings.from_env()
        self.assertEqual(1234, settings.WP10DB_PORT)
        self.assertEqual(["http://a", "http://b"], settings.CLIENT_DOMAINS)

    def test_defaults_apply_when_unset(self):
        with patch.dict("os.environ", {}, clear=True):
            settings = Settings.from_env()
        self.assertEqual("enwp10_dev", settings.WP10DB_DB)
        self.assertEqual(Environment.DEVELOPMENT, settings.ENV)

    @patch.dict("os.environ", {"WP10DB_PORT": "not_a_number"}, clear=False)
    def test_raises_on_invalid_int(self):
        with self.assertRaises(RuntimeError) as ctx:
            Settings.from_env()
        self.assertIn("WP10DB_PORT", str(ctx.exception))

    def test_production_missing_required_names_all_keys(self):
        with patch.dict("os.environ", {"WP1_ENV": "production"}, clear=True):
            with self.assertRaises(RuntimeError) as ctx:
                Settings.from_env()
        self.assertIn("SESSION_SECRET_KEY", str(ctx.exception))
        self.assertIn("MAILGUN_API_KEY", str(ctx.exception))

    def test_production_requires_explicit_values_not_defaults(self):
        # WIKIDB_USER has a development default; production must still
        # require it to be explicitly set.
        with patch.dict("os.environ", {"WP1_ENV": "production"}, clear=True):
            with self.assertRaises(RuntimeError) as ctx:
                Settings.from_env()
        self.assertIn("WIKIDB_USER", str(ctx.exception))

    def test_oauth_mode_requires_oauth_keys(self):
        with patch.dict("os.environ", {"ZIMFARM_AUTH_MODE": "oauth"}, clear=True):
            with self.assertRaises(RuntimeError) as ctx:
                Settings.from_env()
        self.assertIn("ZIMFARM_OAUTH_CLIENT_ID", str(ctx.exception))

    def test_frozen(self):
        settings = Settings()
        with self.assertRaises(attrs.exceptions.FrozenInstanceError):
            settings.WP10DB_DB = "other"


class OverrideSettingsTest(unittest.TestCase):

    def test_override_kwargs_scoped_and_restored(self):
        before = get_settings()
        with override_settings(ZIMFARM_CACHE_URL="https://wasabi.fake/bucket"):
            self.assertEqual(
                "https://wasabi.fake/bucket", get_settings().ZIMFARM_CACHE_URL
            )
        self.assertIs(before, get_settings())

    def test_override_full_instance(self):
        custom = Settings(ENV=Environment.TEST, CONF_LANG="ar")
        with override_settings(custom):
            self.assertEqual("ar", get_settings().CONF_LANG)

    def test_restores_on_exception(self):
        before = get_settings()
        with self.assertRaises(ValueError):
            with override_settings(CONF_LANG="xx"):
                raise ValueError()
        self.assertIs(before, get_settings())

    def test_nested_overrides(self):
        with override_settings(CONF_LANG="ar"):
            with override_settings(CONF_LANG="fr"):
                self.assertEqual("fr", get_settings().CONF_LANG)
            self.assertEqual("ar", get_settings().CONF_LANG)


class ExampleFileTest(unittest.TestCase):

    def test_committed_example_matches_schema(self):
        committed = (
            Path(wp1.config.__file__).resolve().parent.parent / ".env.example"
        ).read_text()
        self.assertEqual(
            generate_example(),
            committed,
            ".env.example is out of date. Run: pipenv run python -m wp1.config",
        )
