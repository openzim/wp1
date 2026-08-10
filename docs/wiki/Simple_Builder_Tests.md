# Simple Builder Tests

> 17 nodes

## Key Concepts

- **SimpleBuilderTest** (21 connections) — `wp1/selection/models/simple_test.py`
- **.test_materialize()** (2 connections) — `wp1/selection/models/simple_test.py`
- **.test_materialize_disallows_invalid()** (2 connections) — `wp1/selection/models/simple_test.py`
- **.setUp()** (1 connections) — `wp1/selection/models/simple_test.py`
- **.test_build()** (1 connections) — `wp1/selection/models/simple_test.py`
- **.test_build_unrecognized_content_type()** (1 connections) — `wp1/selection/models/simple_test.py`
- **.test_build_incorrect_params()** (1 connections) — `wp1/selection/models/simple_test.py`
- **.test_build_ignores_unwanted_params()** (1 connections) — `wp1/selection/models/simple_test.py`
- **.test_build_ignores_comments()** (1 connections) — `wp1/selection/models/simple_test.py`
- **.test_build_ignores_whitespace()** (1 connections) — `wp1/selection/models/simple_test.py`
- **.test_build_decodes_utf8_and_url_encoding()** (1 connections) — `wp1/selection/models/simple_test.py`
- **.test_validate_items()** (1 connections) — `wp1/selection/models/simple_test.py`
- **.test_validate_empty_items()** (1 connections) — `wp1/selection/models/simple_test.py`
- **.test_validate_whitespace_lines_ignored()** (1 connections) — `wp1/selection/models/simple_test.py`
- **.test_validate_comments_ignored()** (1 connections) — `wp1/selection/models/simple_test.py`
- **.test_validate_max_size()** (1 connections) — `wp1/selection/models/simple_test.py`
- **.test_non_en_url_stripping()** (1 connections) — `wp1/selection/models/simple_test.py`

## Relationships

- [Selection Builder Framework](Selection_Builder_Framework.md) (3 shared connections)
- [Abstract Builder Tests](Abstract_Builder_Tests.md) (2 shared connections)
- [DB Test Harness](DB_Test_Harness.md) (1 shared connections)
- [Builder Model & Errors](Builder_Model_%26_Errors.md) (1 shared connections)

## Source Files

- `wp1/selection/models/simple_test.py`

## Audit Trail

- EXTRACTED: 35 (90%)
- INFERRED: 4 (10%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
