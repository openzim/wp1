# Log Processing Tests

> 30 nodes

## Key Concepts

- **LogsTest** (31 connections) — `wp1/logs_test.py`
- **patch** (10 connections)
- **.\_logs()** (9 connections) — `wp1/logs_test.py`
- **.\_move_logs()** (7 connections) — `wp1/logs_test.py`
- **.setUp()** (5 connections) — `wp1/logs_test.py`
- **.\_insert_moves()** (4 connections) — `wp1/logs_test.py`
- **.test_calculate_logs_to_update_values()** (4 connections) — `wp1/logs_test.py`
- **.\_insert_logs()** (3 connections) — `wp1/logs_test.py`
- **.test_get_section_data()** (3 connections) — `wp1/logs_test.py`
- **.test_section_for_date()** (3 connections) — `wp1/logs_test.py`
- **.test_generate_log_edits()** (3 connections) — `wp1/logs_test.py`
- **.\_insert_revids()** (2 connections) — `wp1/logs_test.py`
- **.test_get_revid()** (2 connections) — `wp1/logs_test.py`
- **.test_calculate_logs_to_update_keys()** (2 connections) — `wp1/logs_test.py`
- **.test_get_section_categories()** (2 connections) — `wp1/logs_test.py`
- **.test_upload_log_page_for_project()** (2 connections) — `wp1/logs_test.py`
- **.test_upload_log_page_for_project_no_logs()** (2 connections) — `wp1/logs_test.py`
- **.test_upload_log_page_no_logs_live_page_has_recent_sections_skips()** (2 connections) — `wp1/logs_test.py`
- **.test_upload_log_page_no_logs_live_page_only_old_sections_saves()** (2 connections) — `wp1/logs_test.py`
- **.test_upload_log_page_live_page_date_missing_from_logs_skips()** (2 connections) — `wp1/logs_test.py`
- **.test_upload_log_page_live_page_dates_all_in_logs_saves()** (2 connections) — `wp1/logs_test.py`
- **.test_upload_log_page_for_project_huge_text()** (2 connections) — `wp1/logs_test.py`
- **.test_upload_log_page_for_project_huge_give_up()** (2 connections) — `wp1/logs_test.py`
- **.test_get_logs()** (1 connections) — `wp1/logs_test.py`
- **.test_move_target()** (1 connections) — `wp1/logs_test.py`
- _... and 5 more nodes in this community_

## Relationships

- [Log Model](Log_Model.md) (4 shared connections)
- [Page Move Logic Tests](Page_Move_Logic_Tests.md) (1 shared connections)

## Source Files

- `wp1/logs_test.py`

## Audit Trail

- EXTRACTED: 111 (98%)
- INFERRED: 2 (2%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
