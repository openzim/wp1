# Builders Web Endpoints

> 24 nodes

## Key Concepts

- **get_db()** (43 connections) — `wp1/web/db.py`
- **builders.py** (41 connections) — `wp1/web/builders.py`
- **authenticate()** (16 connections) — `wp1/web/__init__.py`
- **route** (13 connections)
- **\_create_or_update_builder()** (9 connections) — `wp1/web/builders.py`
- **delete_schedule_for_builder()** (9 connections) — `wp1/web/builders.py`
- **get_builder()** (8 connections) — `wp1/web/builders.py`
- **latest_selection_url()** (7 connections) — `wp1/logic/builder.py`
- **update_zimfarm_status()** (7 connections) — `wp1/web/builders.py`
- **latest_selection_article_count_for_builder()** (6 connections) — `wp1/web/builders.py`
- **create_zim_file_for_builder()** (6 connections) — `wp1/web/builders.py`
- **create_builder()** (5 connections) — `wp1/web/builders.py`
- **update_builder()** (5 connections) — `wp1/web/builders.py`
- **get_list_data()** (5 connections) — `wp1/web/selection.py`
- **get_builder_delete_impact()** (4 connections) — `wp1/web/builders.py`
- **delete_builder()** (4 connections) — `wp1/web/builders.py`
- **latest_selection_for_builder()** (4 connections) — `wp1/web/builders.py`
- **latest_zimfarm_selection_for_builder()** (4 connections) — `wp1/web/builders.py`
- **zimfarm_status()** (4 connections) — `wp1/web/builders.py`
- **latest_zim_file_for_builder()** (4 connections) — `wp1/web/builders.py`
- **Returns the raw S3-like storage URL for the latest selection for the given…** (1 connections) — `wp1/logic/builder.py`
- **web/**init**.py** (1 connections) — `wp1/web/__init__.py`
- **Delete an active recurring schedule for a builder.** (1 connections) — `wp1/web/builders.py`
- **route** (1 connections)

## Relationships

- [Builder & Selection Logic](Builder_%26_Selection_Logic.md) (18 shared connections)
- [Projects Web Endpoints](Projects_Web_Endpoints.md) (13 shared connections)
- [ZIM Email Endpoints](ZIM_Email_Endpoints.md) (12 shared connections)
- [Dev Project Stubs](Dev_Project_Stubs.md) (7 shared connections)
- [Zimfarm Integration](Zimfarm_Integration.md) (7 shared connections)
- [Job Queues](Job_Queues.md) (4 shared connections)
- [OAuth Endpoints](OAuth_Endpoints.md) (4 shared connections)
- [ZIM Schedules & Emails](ZIM_Schedules_%26_Emails.md) (3 shared connections)
- [Environment & Credentials Config](Environment_%26_Credentials_Config.md) (2 shared connections)
- [ZIM Task Tracking](ZIM_Task_Tracking.md) (2 shared connections)
- [Storage Test](Storage_Test.md) (2 shared connections)
- [Active Schedule Tests](Active_Schedule_Tests.md) (2 shared connections)

## Source Files

- `wp1/logic/builder.py`
- `wp1/web/__init__.py`
- `wp1/web/builders.py`
- `wp1/web/db.py`
- `wp1/web/selection.py`

## Audit Trail

- EXTRACTED: 208 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
