# Config Parsing Tests

> 24 nodes

## Key Concepts

- **dict** (21 connections)
- **config_test.py** (11 connections) — `wp1/config_test.py`
- **\_getenv_list()** (10 connections) — `wp1/config.py`
- **\_getenv()** (9 connections) — `wp1/config.py`
- **GetenvListTest** (9 connections) — `wp1/config_test.py`
- **\_getenv_int()** (8 connections) — `wp1/config.py`
- **GetenvIntTest** (7 connections) — `wp1/config_test.py`
- **GetenvTest** (6 connections) — `wp1/config_test.py`
- **.test_returns_value_when_set()** (3 connections) — `wp1/config_test.py`
- **.test_returns_default_when_not_set()** (3 connections) — `wp1/config_test.py`
- **.test_returns_none_when_not_set_and_no_default()** (3 connections) — `wp1/config_test.py`
- **.test_raises_when_required_and_missing()** (3 connections) — `wp1/config_test.py`
- **.test_returns_int_value()** (3 connections) — `wp1/config_test.py`
- **.test_returns_none_when_not_set()** (3 connections) — `wp1/config_test.py`
- **.test_returns_default_as_int()** (3 connections) — `wp1/config_test.py`
- **.test_raises_on_invalid_int()** (3 connections) — `wp1/config_test.py`
- **.test_raises_on_empty_string()** (3 connections) — `wp1/config_test.py`
- **.test_parses_comma_separated()** (3 connections) — `wp1/config_test.py`
- **.test_strips_whitespace()** (3 connections) — `wp1/config_test.py`
- **.test_single_item()** (3 connections) — `wp1/config_test.py`
- **.test_empty_string_returns_empty_list()** (3 connections) — `wp1/config_test.py`
- **.test_returns_default_when_not_set()** (3 connections) — `wp1/config_test.py`
- **.test_returns_empty_list_when_not_set_and_no_default()** (3 connections) — `wp1/config_test.py`
- **.test_skips_empty_entries()** (3 connections) — `wp1/config_test.py`

## Relationships

- [Environment & Credentials Config](Environment_%26_Credentials_Config.md) (9 shared connections)
- [Config Test](Config_Test.md) (8 shared connections)

## Source Files

- `wp1/config.py`
- `wp1/config_test.py`

## Audit Trail

- EXTRACTED: 126 (98%)
- INFERRED: 3 (2%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
