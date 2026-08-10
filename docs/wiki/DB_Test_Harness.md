# DB Test Harness

> 37 nodes

## Key Concepts

- **BaseWpOneDbTest** (115 connections) — `wp1/base_db_test.py`
- **base_db_test.py** (60 connections) — `wp1/base_db_test.py`
- **BaseWikiDbTest** (29 connections) — `wp1/base_db_test.py`
- **queues_test.py** (11 connections) — `wp1/queues_test.py`
- **\_reset_tables()** (8 connections) — `wp1/base_db_test.py`
- **WpOneAssertions** (7 connections) — `wp1/base_db_test.py`
- **maintenance_test.py** (7 connections) — `wp1/maintenance_test.py`
- **scores_test.py** (7 connections) — `wp1/scores_test.py`
- **.\_setup_wp_one_db()** (6 connections) — `wp1/base_db_test.py`
- **.\_setup_wiki_db()** (6 connections) — `wp1/base_db_test.py`
- **parse_sql()** (5 connections) — `wp1/base_db_test.py`
- **\_ensure_schema()** (5 connections) — `wp1/base_db_test.py`
- **base_custom_table_test.py** (5 connections) — `wp1/custom_tables/base_custom_table_test.py`
- **us_roads_test.py** (5 connections) — `wp1/custom_tables/us_roads_test.py`
- **UsRoadsCustomTableTest** (5 connections) — `wp1/custom_tables/us_roads_test.py`
- **wp10/builder_test.py** (5 connections) — `wp1/models/wp10/builder_test.py`
- **zim_schedule_test.py** (5 connections) — `wp1/models/wp10/zim_schedule_test.py`
- **.\_setup_redis_db()** (4 connections) — `wp1/base_db_test.py`
- **.setUp()** (4 connections) — `wp1/base_db_test.py`
- **users_test.py** (4 connections) — `wp1/logic/users_test.py`
- **\_table_names()** (3 connections) — `wp1/base_db_test.py`
- **\_seed_stmts()** (3 connections) — `wp1/base_db_test.py`
- **\_auto_increment_tables()** (3 connections) — `wp1/base_db_test.py`
- **.setUp()** (3 connections) — `wp1/base_db_test.py`
- **\_read_auto_increments()** (2 connections) — `wp1/base_db_test.py`
- _... and 12 more nodes in this community_

## Relationships

- [Assessment Tables & Categories](Assessment_Tables_%26_Categories.md) (17 shared connections)
- [Page Move Logic Tests](Page_Move_Logic_Tests.md) (14 shared connections)
- [Selection Builder Framework](Selection_Builder_Framework.md) (14 shared connections)
- [Rating Model Tests](Rating_Model_Tests.md) (13 shared connections)
- [ZIM Schedules & Emails](ZIM_Schedules_%26_Emails.md) (13 shared connections)
- [Project & Page Models](Project_%26_Page_Models.md) (13 shared connections)
- [Environment & Credentials Config](Environment_%26_Credentials_Config.md) (10 shared connections)
- [Selection & Meta Builder](Selection_%26_Meta_Builder.md) (10 shared connections)
- [Builder Model & Errors](Builder_Model_%26_Errors.md) (10 shared connections)
- [Constants & Utilities](Constants_%26_Utilities.md) (8 shared connections)
- [Custom Tables](Custom_Tables.md) (7 shared connections)
- [ZIM Task Tracking](ZIM_Task_Tracking.md) (6 shared connections)

## Source Files

- `wp1/base_db_test.py`
- `wp1/custom_tables/base_custom_table_test.py`
- `wp1/custom_tables/us_roads_test.py`
- `wp1/logic/users_test.py`
- `wp1/maintenance_test.py`
- `wp1/models/wp10/builder_test.py`
- `wp1/models/wp10/zim_schedule_test.py`
- `wp1/queues_test.py`
- `wp1/scores_test.py`

## Audit Trail

- EXTRACTED: 239 (72%)
- INFERRED: 94 (28%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
