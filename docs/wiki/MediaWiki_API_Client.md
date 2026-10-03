# MediaWiki API Client

> 19 nodes

## Key Concepts

- **connect()** (26 connections) — `wp1/wp10_db.py`
- **api.py** (15 connections) — `wp1/api.py`
- **update_log_page_for_project()** (11 connections) — `wp1/logs.py`
- **get_page()** (10 connections) — `wp1/api.py`
- **api/page.py** (9 connections) — `wp1/logic/api/page.py`
- **login()** (7 connections) — `wp1/api.py`
- **save_page()** (7 connections) — `wp1/api.py`
- **upload_project_table()** (7 connections) — `wp1/tables.py`
- **upload_global_table()** (7 connections) — `wp1/tables.py`
- **articles.py** (6 connections) — `wp1/web/articles.py`
- **update_global_project_count()** (5 connections) — `wp1/logic/project.py`
- **redirect()** (4 connections) — `wp1/web/articles.py`
- **get_revision_id_by_timestamp()** (3 connections) — `wp1/api.py`
- **get_redirect()** (3 connections) — `wp1/logic/api/page.py`
- **get_moves()** (3 connections) — `wp1/logic/api/page.py`
- **create_wikicode()** (3 connections) — `wp1/tables.py`
- **get_credentials()** (2 connections) — `wp1/api.py`
- **route** (1 connections)
- **Connection** (1 connections)

## Relationships

- [Log Upload](Log_Upload.md) (8 shared connections)
- [Constants & Utilities](Constants_%26_Utilities.md) (6 shared connections)
- [Project & Rating Updates](Project_%26_Rating_Updates.md) (6 shared connections)
- [Tables](Tables.md) (6 shared connections)
- [20220818 01 5X0T9 Add Object](20220818_01_5X0T9_Add_Object.md) (6 shared connections)
- [Page Logic](Page_Logic.md) (3 shared connections)
- [Init Test](Init_Test.md) (3 shared connections)
- [Builder & Selection Logic](Builder_%26_Selection_Logic.md) (3 shared connections)
- [Maintenance](Maintenance.md) (3 shared connections)
- [Projects Web Endpoints](Projects_Web_Endpoints.md) (2 shared connections)
- [ZIM Email Endpoints](ZIM_Email_Endpoints.md) (2 shared connections)
- [Pageview Scores](Pageview_Scores.md) (2 shared connections)

## Source Files

- `wp1/api.py`
- `wp1/logic/api/page.py`
- `wp1/logic/project.py`
- `wp1/logs.py`
- `wp1/tables.py`
- `wp1/web/articles.py`
- `wp1/wp10_db.py`

## Audit Trail

- EXTRACTED: 130 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
