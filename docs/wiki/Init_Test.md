# Init Test

> 12 nodes

## Key Concepts

- **wp10_db.py** (14 connections) — `wp1/wp10_db.py`
- **upload_custom_table_by_name()** (9 connections) — `wp1/custom_tables/__init__.py`
- **CustomTablesInitTest** (7 connections) — `wp1/custom_tables/init_test.py`
- **custom_tables/**init**.py** (6 connections) — `wp1/custom_tables/__init__.py`
- **init_test.py** (5 connections) — `wp1/custom_tables/init_test.py`
- **all_custom_table_names()** (4 connections) — `wp1/custom_tables/__init__.py`
- **patch** (4 connections)
- **.test_upload_custom_table_by_name()** (3 connections) — `wp1/custom_tables/init_test.py`
- **.test_upload_custom_table_by_name_no_entry()** (3 connections) — `wp1/custom_tables/init_test.py`
- **.test_upload_custom_table_by_name_bad_json()** (3 connections) — `wp1/custom_tables/init_test.py`
- **.test_upload_custom_table_by_name_bad_module_path()** (3 connections) — `wp1/custom_tables/init_test.py`
- **.test_all_custom_table_names()** (2 connections) — `wp1/custom_tables/init_test.py`

## Relationships

- [20220818 01 5X0T9 Add Object](20220818_01_5X0T9_Add_Object.md) (3 shared connections)
- [MediaWiki API Client](MediaWiki_API_Client.md) (3 shared connections)
- [DB Test Harness](DB_Test_Harness.md) (3 shared connections)
- [Job Queues](Job_Queues.md) (2 shared connections)
- [Environment & Credentials Config](Environment_%26_Credentials_Config.md) (2 shared connections)
- [Custom Tables](Custom_Tables.md) (1 shared connections)
- [DB Connection Tests](DB_Connection_Tests.md) (1 shared connections)
- [Builder & Selection Logic](Builder_%26_Selection_Logic.md) (1 shared connections)
- [Project & Rating Updates](Project_%26_Rating_Updates.md) (1 shared connections)
- [Log Upload](Log_Upload.md) (1 shared connections)
- [Maintenance](Maintenance.md) (1 shared connections)
- [Review](Review.md) (1 shared connections)

## Source Files

- `wp1/custom_tables/__init__.py`
- `wp1/custom_tables/init_test.py`
- `wp1/wp10_db.py`

## Audit Trail

- EXTRACTED: 61 (97%)
- INFERRED: 2 (3%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
