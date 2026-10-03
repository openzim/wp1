# Log Upload

> 18 nodes

## Key Concepts

- **logs.py** (31 connections) — `wp1/logs.py`
- **get_current_datetime()** (9 connections) — `wp1/time.py`
- **get_section_data()** (7 connections) — `wp1/logs.py`
- **int_to_ns()** (6 connections) — `wp1/logic/util.py`
- **calculate_logs_to_update()** (5 connections) — `wp1/logs.py`
- **name_for_article()** (3 connections) — `wp1/logs.py`
- **talk_page_for_article()** (3 connections) — `wp1/logs.py`
- **section_for_date()** (3 connections) — `wp1/logs.py`
- **generate_log_edits()** (3 connections) — `wp1/logs.py`
- **live_page_dates_missing_from_logs()** (3 connections) — `wp1/logs.py`
- **ns_to_int()** (2 connections) — `wp1/logic/util.py`
- **log_page_name()** (2 connections) — `wp1/logs.py`
- **move_target()** (2 connections) — `wp1/logs.py`
- **get_revid()** (2 connections) — `wp1/logs.py`
- **get_section_categories()** (2 connections) — `wp1/logs.py`
- **datetime** (2 connections)
- **Return a dictionary of datetime -> list of log objects that should be uploaded…** (1 connections) — `wp1/logs.py`
- **Dates of log sections on the live page that are inside the 7-day window but…** (1 connections) — `wp1/logs.py`

## Relationships

- [Constants & Utilities](Constants_%26_Utilities.md) (9 shared connections)
- [MediaWiki API Client](MediaWiki_API_Client.md) (8 shared connections)
- [Log Model](Log_Model.md) (7 shared connections)
- [20220818 01 5X0T9 Add Object](20220818_01_5X0T9_Add_Object.md) (3 shared connections)
- [Pageview Scores](Pageview_Scores.md) (2 shared connections)
- [Page Logic](Page_Logic.md) (1 shared connections)
- [Environment & Credentials Config](Environment_%26_Credentials_Config.md) (1 shared connections)
- [Init Test](Init_Test.md) (1 shared connections)
- [Job Queues](Job_Queues.md) (1 shared connections)

## Source Files

- `wp1/logic/util.py`
- `wp1/logs.py`
- `wp1/time.py`

## Audit Trail

- EXTRACTED: 87 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
