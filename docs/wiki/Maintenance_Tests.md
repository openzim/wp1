# Maintenance Tests

> 16 nodes

## Key Concepts

- **Queue** (12 connections)
- **MaintenanceTest** (11 connections) — `wp1/maintenance_test.py`
- **patch** (8 connections)
- **enqueue_global()** (4 connections) — `wp1/maintenance.py`
- **RateLimitQueue** (3 connections) — `rate_limit_queue.py`
- **.test_enqueue_global_production()** (3 connections) — `wp1/maintenance_test.py`
- **.test_enqueue_global_development()** (3 connections) — `wp1/maintenance_test.py`
- **.test_update_global_articles_stops_inflight_jobs()** (3 connections) — `wp1/maintenance_test.py`
- **.test_update_global_articles_survives_stop_command_failure()** (3 connections) — `wp1/maintenance_test.py`
- **rate_limit_queue.py** (2 connections) — `rate_limit_queue.py`
- **.test_enqueue_all()** (2 connections) — `wp1/maintenance_test.py`
- **.test_update_global_articles_stops_workers_during_rebuild()** (2 connections) — `wp1/maintenance_test.py`
- **.test_update_global_articles_restarts_workers_after_failure()** (2 connections) — `wp1/maintenance_test.py`
- **.test_update_global_articles_aborts_if_workers_cannot_be_stopped()** (2 connections) — `wp1/maintenance_test.py`
- **.dequeue_any()** (1 connections) — `rate_limit_queue.py`
- **Daily (05:00 UTC): enqueue the global table upload and project count.** (1 connections) — `wp1/maintenance.py`

## Relationships

- [Job Queues](Job_Queues.md) (4 shared connections)
- [Maintenance](Maintenance.md) (2 shared connections)
- [DB Test Harness](DB_Test_Harness.md) (2 shared connections)
- [Constants & Utilities](Constants_%26_Utilities.md) (1 shared connections)
- [Queue Tests](Queue_Tests.md) (1 shared connections)
- [20220818 01 5X0T9 Add Object](20220818_01_5X0T9_Add_Object.md) (1 shared connections)
- [Environment & Credentials Config](Environment_%26_Credentials_Config.md) (1 shared connections)

## Source Files

- `rate_limit_queue.py`
- `wp1/maintenance.py`
- `wp1/maintenance_test.py`

## Audit Trail

- EXTRACTED: 44 (71%)
- INFERRED: 18 (29%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
