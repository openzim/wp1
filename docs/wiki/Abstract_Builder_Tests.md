# Abstract Builder Tests

> 19 nodes

## Key Concepts

- **get_first_selection()** (26 connections) — `wp1/base_db_test.py`
- **AbstractBuilderTest** (25 connections) — `wp1/selection/abstract_builder_test.py`
- **patch** (4 connections)
- **.test_materialize_selection_id()** (3 connections) — `wp1/selection/abstract_builder_test.py`
- **.test_materialize_selection_object_key()** (3 connections) — `wp1/selection/abstract_builder_test.py`
- **.test_materialize_selection_updated_at()** (3 connections) — `wp1/selection/abstract_builder_test.py`
- **.test_materialize_retryable_error()** (3 connections) — `wp1/selection/abstract_builder_test.py`
- **.test_materialize_retryable_error_messages()** (3 connections) — `wp1/selection/abstract_builder_test.py`
- **.test_materialize_fatal_error()** (3 connections) — `wp1/selection/abstract_builder_test.py`
- **.test_materialize_fatal_error_messages()** (3 connections) — `wp1/selection/abstract_builder_test.py`
- **.test_materialize_no_context_messages()** (3 connections) — `wp1/selection/abstract_builder_test.py`
- **.test_materialize_extra_error_data()** (3 connections) — `wp1/selection/abstract_builder_test.py`
- **.test_materialize_suppressed_message()** (3 connections) — `wp1/selection/abstract_builder_test.py`
- **.test_materialize_validates_before_building()** (3 connections) — `wp1/selection/abstract_builder_test.py`
- **.test_materialize_creates_selection()** (2 connections) — `wp1/selection/abstract_builder_test.py`
- **.test_materialize_uploads_to_s3()** (2 connections) — `wp1/selection/abstract_builder_test.py`
- **.test_materialize_version()** (2 connections) — `wp1/selection/abstract_builder_test.py`
- **.test_materialize_passes_builder_context_to_validate()** (2 connections) — `wp1/selection/abstract_builder_test.py`
- **.test_materialize_update_article_count()** (2 connections) — `wp1/selection/abstract_builder_test.py`

## Relationships

- [Builder Model & Errors](Builder_Model_%26_Errors.md) (15 shared connections)
- [Selection Builder Framework](Selection_Builder_Framework.md) (6 shared connections)
- [DB Test Harness](DB_Test_Harness.md) (2 shared connections)
- [Selection & Meta Builder](Selection_%26_Meta_Builder.md) (2 shared connections)
- [Simple Builder Tests](Simple_Builder_Tests.md) (2 shared connections)
- [Book Test](Book_Test.md) (1 shared connections)
- [Petscan Builder Tests](Petscan_Builder_Tests.md) (1 shared connections)
- [SPARQL Builder Tests](SPARQL_Builder_Tests.md) (1 shared connections)

## Source Files

- `wp1/base_db_test.py`
- `wp1/selection/abstract_builder_test.py`

## Audit Trail

- EXTRACTED: 91 (93%)
- INFERRED: 7 (7%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
