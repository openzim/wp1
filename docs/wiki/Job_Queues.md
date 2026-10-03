# Job Queues

> 25 nodes

## Key Concepts

- **queues.py** (43 connections) — `wp1/queues.py`
- **update()** (9 connections) — `wp1/web/projects.py`
- **enqueue_all_projects()** (7 connections) — `wp1/queues.py`
- **\_get_queues()** (6 connections) — `wp1/queues.py`
- **enqueue_assessment_cache_warming()** (5 connections) — `wp1/queues.py`
- **enqueue_single_project()** (5 connections) — `wp1/queues.py`
- **enqueue_project()** (5 connections) — `wp1/queues.py`
- **enqueue_materialize()** (5 connections) — `wp1/queues.py`
- **schedule_recurring_zimfarm_task()** (5 connections) — `wp1/queues.py`
- **cancel_scheduled_job()** (5 connections) — `wp1/queues.py`
- **Redis** (4 connections)
- **enqueue_multiple_projects()** (4 connections) — `wp1/queues.py`
- **next_update_time()** (4 connections) — `wp1/queues.py`
- **mark_project_manual_update_time()** (4 connections) — `wp1/queues.py`
- **\_get_materializer_queue()** (3 connections) — `wp1/queues.py`
- **\_get_zimfile_scheduling_queue()** (3 connections) — `wp1/queues.py`
- **\_get_assessment_cache_queue()** (3 connections) — `wp1/queues.py`
- **enqueue_custom_table()** (3 connections) — `wp1/queues.py`
- **\_manual_key()** (3 connections) — `wp1/queues.py`
- **\_update_job_status_key()** (3 connections) — `wp1/queues.py`
- **get_project_queue_status()** (3 connections) — `wp1/queues.py`
- **set_project_update_job_id()** (3 connections) — `wp1/queues.py`
- **Enqueue a one-off assessment-cache warming job to run immediately. Called on…** (1 connections) — `wp1/queues.py`
- **Schedule a recurring zimfarm task, first running at scheduled_time and then…** (1 connections) — `wp1/queues.py`
- **Cancel a scheduled RQ job by its job ID. Returns True when the job is cancelled…** (1 connections) — `wp1/queues.py`

## Relationships

- [20220818 01 5X0T9 Add Object](20220818_01_5X0T9_Add_Object.md) (6 shared connections)
- [ZIM Schedules & Emails](ZIM_Schedules_%26_Emails.md) (6 shared connections)
- [Projects Web Endpoints](Projects_Web_Endpoints.md) (6 shared connections)
- [Environment & Credentials Config](Environment_%26_Credentials_Config.md) (4 shared connections)
- [Project & Rating Updates](Project_%26_Rating_Updates.md) (4 shared connections)
- [Builders Web Endpoints](Builders_Web_Endpoints.md) (4 shared connections)
- [Maintenance Tests](Maintenance_Tests.md) (4 shared connections)
- [Builder & Selection Logic](Builder_%26_Selection_Logic.md) (3 shared connections)
- [Init Test](Init_Test.md) (2 shared connections)
- [Maintenance](Maintenance.md) (2 shared connections)
- [Constants & Utilities](Constants_%26_Utilities.md) (1 shared connections)
- [Log Upload](Log_Upload.md) (1 shared connections)

## Source Files

- `wp1/queues.py`
- `wp1/web/projects.py`

## Audit Trail

- EXTRACTED: 134 (97%)
- INFERRED: 4 (3%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
