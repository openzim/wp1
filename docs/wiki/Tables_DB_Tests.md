# Tables DB Tests

> 26 nodes

## Key Concepts

- **TablesDbTest** (27 connections) — `wp1/tables_test.py`
- **.setUp()** (4 connections) — `wp1/tables_test.py`
- **patch** (4 connections)
- **.\_insert_ratings()** (3 connections) — `wp1/tables_test.py`
- **.\_setup_global_articles()** (2 connections) — `wp1/tables_test.py`
- **.\_setup_project_categories()** (2 connections) — `wp1/tables_test.py`
- **.test_upload_project_table()** (2 connections) — `wp1/tables_test.py`
- **.test_upload_global_table()** (2 connections) — `wp1/tables_test.py`
- **.test_empty_cache()** (2 connections) — `wp1/tables_test.py`
- **.test_full_cache()** (2 connections) — `wp1/tables_test.py`
- **.test_get_global_stats()** (1 connections) — `wp1/tables_test.py`
- **.test_get_project_stats()** (1 connections) — `wp1/tables_test.py`
- **.test_db_project_categories()** (1 connections) — `wp1/tables_test.py`
- **.test_get_project_categories()** (1 connections) — `wp1/tables_test.py`
- **.test_data_for_stats()** (1 connections) — `wp1/tables_test.py`
- **.test_generate_table_data_removes_cols()** (1 connections) — `wp1/tables_test.py`
- **.test_generate_table_data_removes_rows()** (1 connections) — `wp1/tables_test.py`
- **.test_generate_table_data_adds_assessed_when_unassessed()** (1 connections) — `wp1/tables_test.py`
- **.test_generate_table_data_adds_assessed_when_no_unassessed()** (1 connections) — `wp1/tables_test.py`
- **.test_generate_table_data_totals()** (1 connections) — `wp1/tables_test.py`
- **.test_generate_table_data_ordered_cols()** (1 connections) — `wp1/tables_test.py`
- **.test_generate_table_data_ordered_rows()** (1 connections) — `wp1/tables_test.py`
- **.test_generate_table_data_labels()** (1 connections) — `wp1/tables_test.py`
- **.test_generate_table_data_table_overrides()** (1 connections) — `wp1/tables_test.py`
- **.test_generate_project_table_data()** (1 connections) — `wp1/tables_test.py`
- _... and 1 more nodes in this community_

## Relationships

- [Assessment Tables & Categories](Assessment_Tables_%26_Categories.md) (5 shared connections)
- [Rating Model Tests](Rating_Model_Tests.md) (2 shared connections)
- [DB Test Harness](DB_Test_Harness.md) (1 shared connections)

## Source Files

- `wp1/tables_test.py`

## Audit Trail

- EXTRACTED: 62 (94%)
- INFERRED: 4 (6%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
