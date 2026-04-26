import unittest
from unittest.mock import patch

from wp1.config import _getenv, _getenv_int, _getenv_list, _resolve_env
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
    def test_test(self):
        self.assertEqual(Environment.TEST, _resolve_env())

    @patch.dict("os.environ", {"WP1_ENV": "DEVELOPMENT"}, clear=False)
    def test_case_insensitive(self):
        self.assertEqual(Environment.DEVELOPMENT, _resolve_env())

    @patch.dict("os.environ", {"WP1_ENV": "staging"}, clear=False)
    def test_raises_on_invalid_value(self):
        with self.assertRaises(RuntimeError) as ctx:
            _resolve_env()
        self.assertIn("staging", str(ctx.exception))
