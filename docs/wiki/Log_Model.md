# Log Model

> 22 nodes

## Key Concepts

- **Log** (25 connections) — `wp1/models/wp10/log.py`
- **logic/log.py** (17 connections) — `wp1/logic/log.py`
- **wp10/log.py** (10 connections) — `wp1/models/wp10/log.py`
- **20250330_01_zaRQa-migrate-last-7-days-of-logs.py** (9 connections) — `db/migrations/20250330_01_zaRQa-migrate-last-7-days-of-logs.py`
- **get_logs()** (9 connections) — `wp1/logic/log.py`
- **logs_test.py** (7 connections) — `wp1/logs_test.py`
- **insert_or_update()** (6 connections) — `wp1/logic/log.py`
- **log_test.py** (6 connections) — `wp1/models/wp10/log_test.py`
- **migrate_logs()** (5 connections) — `db/migrations/20250330_01_zaRQa-migrate-last-7-days-of-logs.py`
- **ModelsLogTest** (5 connections) — `wp1/models/wp10/log_test.py`
- **gen_redis_log_key()** (4 connections) — `wp1/redis_db.py`
- **Redis** (3 connections)
- **datetime** (2 connections)
- **.timestamp_dt()** (2 connections) — `wp1/models/wp10/log.py`
- **.rev_timestamp_dt()** (2 connections) — `wp1/models/wp10/log.py`
- **.setUp()** (2 connections) — `wp1/models/wp10/log_test.py`
- **Migrate last 7 days of logs** (1 connections) — `db/migrations/20250330_01_zaRQa-migrate-last-7-days-of-logs.py`
- **Retrieve logs from Redis matching the given filters.** (1 connections) — `wp1/logic/log.py`
- **s** (1 connections)
- **The timestamp parsed into a datetime.datetime object.** (1 connections) — `wp1/models/wp10/log.py`
- **The revision timestamp parsed into a datetime.datetime object.** (1 connections) — `wp1/models/wp10/log.py`
- **.test_timestamp_dt()** (1 connections) — `wp1/models/wp10/log_test.py`

## Relationships

- [Page Move Logic Tests](Page_Move_Logic_Tests.md) (8 shared connections)
- [Log Upload](Log_Upload.md) (7 shared connections)
- [20220818 01 5X0T9 Add Object](20220818_01_5X0T9_Add_Object.md) (5 shared connections)
- [Page Logic](Page_Logic.md) (5 shared connections)
- [Project & Rating Updates](Project_%26_Rating_Updates.md) (4 shared connections)
- [DB Test Harness](DB_Test_Harness.md) (4 shared connections)
- [Log Processing Tests](Log_Processing_Tests.md) (4 shared connections)
- [Constants & Utilities](Constants_%26_Utilities.md) (3 shared connections)
- [Rating Model Tests](Rating_Model_Tests.md) (1 shared connections)
- [Project Assessment Tests](Project_Assessment_Tests.md) (1 shared connections)

## Source Files

- `db/migrations/20250330_01_zaRQa-migrate-last-7-days-of-logs.py`
- `wp1/logic/log.py`
- `wp1/logs_test.py`
- `wp1/models/wp10/log.py`
- `wp1/models/wp10/log_test.py`
- `wp1/redis_db.py`

## Audit Trail

- EXTRACTED: 113 (94%)
- INFERRED: 7 (6%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
