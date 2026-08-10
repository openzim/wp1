# Config Test

> 7 nodes

## Key Concepts

- **\_resolve_env()** (8 connections) — `wp1/config.py`
- **ResolveEnvTest** (7 connections) — `wp1/config_test.py`
- **.test_development()** (3 connections) — `wp1/config_test.py`
- **.test_production()** (3 connections) — `wp1/config_test.py`
- **.test_test()** (3 connections) — `wp1/config_test.py`
- **.test_case_insensitive()** (3 connections) — `wp1/config_test.py`
- **.test_raises_on_invalid_value()** (3 connections) — `wp1/config_test.py`

## Relationships

- [Config Parsing Tests](Config_Parsing_Tests.md) (8 shared connections)
- [Environment & Credentials Config](Environment_%26_Credentials_Config.md) (2 shared connections)

## Source Files

- `wp1/config.py`
- `wp1/config_test.py`

## Audit Trail

- EXTRACTED: 29 (97%)
- INFERRED: 1 (3%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
