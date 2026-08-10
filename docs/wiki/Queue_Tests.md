# Queue Tests

> 24 nodes

## Key Concepts

- **QueuesTest** (26 connections) — `wp1/queues_test.py`
- **patch** (10 connections)
- **.\_zimfile_scheduling_registry()** (6 connections) — `wp1/queues_test.py`
- **.test_enqueue_project_development()** (2 connections) — `wp1/queues_test.py`
- **.test_enqueue_project_production()** (2 connections) — `wp1/queues_test.py`
- **.test_enqueue_single_project()** (2 connections) — `wp1/queues_test.py`
- **.test_enqueue_multipe_projects()** (2 connections) — `wp1/queues_test.py`
- **.test_enqueue_all()** (2 connections) — `wp1/queues_test.py`
- **.test_get_project_queue_status_job_finished()** (2 connections) — `wp1/queues_test.py`
- **.test_enqueue_materialize()** (2 connections) — `wp1/queues_test.py`
- **.test_schedule_recurring_zimfarm_task()** (2 connections) — `wp1/queues_test.py`
- **.test_schedule_recurring_zimfarm_task_single_run()** (2 connections) — `wp1/queues_test.py`
- **.test_cancel_scheduled_job_success()** (2 connections) — `wp1/queues_test.py`
- **.test_cancel_scheduled_job_with_bytes_id()** (2 connections) — `wp1/queues_test.py`
- **.test_cancel_scheduled_job_executing()** (2 connections) — `wp1/queues_test.py`
- **.test_cancel_scheduled_job_failure()** (2 connections) — `wp1/queues_test.py`
- **.test_enqueue_assessment_cache_warming()** (2 connections) — `wp1/queues_test.py`
- **.setUp()** (1 connections) — `wp1/queues_test.py`
- **.tearDown()** (1 connections) — `wp1/queues_test.py`
- **.test_next_update_time_empty()** (1 connections) — `wp1/queues_test.py`
- **.test_next_update_time_after_update()** (1 connections) — `wp1/queues_test.py`
- **.test_get_project_queue_status_no_job()** (1 connections) — `wp1/queues_test.py`
- **.test_cancel_scheduled_job_missing_job()** (1 connections) — `wp1/queues_test.py`
- **.test_cancel_scheduled_job_already_cancelled()** (1 connections) — `wp1/queues_test.py`

## Relationships

- [DB Test Harness](DB_Test_Harness.md) (2 shared connections)
- [Environment & Credentials Config](Environment_%26_Credentials_Config.md) (1 shared connections)
- [Selection Builder Framework](Selection_Builder_Framework.md) (1 shared connections)
- [Maintenance Tests](Maintenance_Tests.md) (1 shared connections)

## Source Files

- `wp1/queues_test.py`

## Audit Trail

- EXTRACTED: 73 (95%)
- INFERRED: 4 (5%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
