# Petscan Builder Tests

> 19 nodes

## Key Concepts

- **PetscanBuilderTest** (20 connections) — `wp1/selection/models/petscan_test.py`
- **patch** (6 connections)
- **.test_materialize()** (3 connections) — `wp1/selection/models/petscan_test.py`
- **.test_build_url_with_whitespace()** (3 connections) — `wp1/selection/models/petscan_test.py`
- **.test_build()** (2 connections) — `wp1/selection/models/petscan_test.py`
- **.test_build_no_format()** (2 connections) — `wp1/selection/models/petscan_test.py`
- **.test_build_other_format()** (2 connections) — `wp1/selection/models/petscan_test.py`
- **.test_build_non_200()** (2 connections) — `wp1/selection/models/petscan_test.py`
- **.test_validate_url_with_whitespace()** (2 connections) — `wp1/selection/models/petscan_test.py`
- **.setUp()** (1 connections) — `wp1/selection/models/petscan_test.py`
- **.test_build_wrong_content_type()** (1 connections) — `wp1/selection/models/petscan_test.py`
- **.test_build_missing_url()** (1 connections) — `wp1/selection/models/petscan_test.py`
- **.test_build_url_not_str()** (1 connections) — `wp1/selection/models/petscan_test.py`
- **.test_validate()** (1 connections) — `wp1/selection/models/petscan_test.py`
- **.test_validate_missing_url()** (1 connections) — `wp1/selection/models/petscan_test.py`
- **.test_validate_not_a_url()** (1 connections) — `wp1/selection/models/petscan_test.py`
- **.test_validate_not_a_petscan_url()** (1 connections) — `wp1/selection/models/petscan_test.py`
- **Test that URLs with leading/trailing whitespace are trimmed and validated.** (1 connections) — `wp1/selection/models/petscan_test.py`
- **Test that URLs with whitespace are trimmed before building.** (1 connections) — `wp1/selection/models/petscan_test.py`

## Relationships

- [Selection Builder Framework](Selection_Builder_Framework.md) (3 shared connections)
- [DB Test Harness](DB_Test_Harness.md) (1 shared connections)
- [Builder Model & Errors](Builder_Model_%26_Errors.md) (1 shared connections)
- [Abstract Builder Tests](Abstract_Builder_Tests.md) (1 shared connections)

## Source Files

- `wp1/selection/models/petscan_test.py`

## Audit Trail

- EXTRACTED: 48 (92%)
- INFERRED: 4 (8%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
