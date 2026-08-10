# Active Schedule Tests

> 20 nodes

## Key Concepts

- **zim_schedules_active_test.py** (13 connections) — `wp1/logic/zim_schedules_active_test.py`
- **find_active_recurring_schedule_for_builder()** (11 connections) — `wp1/logic/zim_schedules.py`
- **delete_zim_schedule()** (11 connections) — `wp1/logic/zim_schedules.py`
- **LogicZimSchedulesActiveTest** (10 connections) — `wp1/logic/zim_schedules_active_test.py`
- **.new_schedule()** (7 connections) — `wp1/logic/zim_schedules_active_test.py`
- **.test_delete_zim_schedule_success()** (7 connections) — `wp1/logic/zim_schedules_active_test.py`
- **.test_delete_zim_schedule_no_rq_job()** (7 connections) — `wp1/logic/zim_schedules_active_test.py`
- **.test_find_active_recurring_schedule_for_builder_with_active_schedule()** (5 connections) — `wp1/logic/zim_schedules_active_test.py`
- **.test_find_active_recurring_schedule_for_builder_no_active_schedule()** (5 connections) — `wp1/logic/zim_schedules_active_test.py`
- **.test_delete_zim_schedule_nonexistent()** (4 connections) — `wp1/logic/zim_schedules_active_test.py`
- **.test_find_active_recurring_schedule_for_builder_no_schedules()** (3 connections) — `wp1/logic/zim_schedules_active_test.py`
- **patch** (3 connections)
- **Returns an active recurring schedule for a builder (remaining_generations > 0).** (1 connections) — `wp1/logic/zim_schedules.py`
- **Deletes a ZIM schedule by canceling the RQ job and removing the database record.** (1 connections) — `wp1/logic/zim_schedules.py`
- **Test finding an active recurring schedule (remaining_generations > 0).** (1 connections) — `wp1/logic/zim_schedules_active_test.py`
- **Test when no active recurring schedule exists.** (1 connections) — `wp1/logic/zim_schedules_active_test.py`
- **Test when no schedules exist for the builder.** (1 connections) — `wp1/logic/zim_schedules_active_test.py`
- **Test successful deletion of a ZIM schedule.** (1 connections) — `wp1/logic/zim_schedules_active_test.py`
- **Test deletion of a non-existent schedule.** (1 connections) — `wp1/logic/zim_schedules_active_test.py`
- **Test deletion of a schedule with no RQ job ID.** (1 connections) — `wp1/logic/zim_schedules_active_test.py`

## Relationships

- [ZIM Schedule Logic](ZIM_Schedule_Logic.md) (12 shared connections)
- [ZIM Schedules & Emails](ZIM_Schedules_%26_Emails.md) (11 shared connections)
- [DB Test Harness](DB_Test_Harness.md) (3 shared connections)
- [Builders Web Endpoints](Builders_Web_Endpoints.md) (2 shared connections)
- [Builder & Selection Logic](Builder_%26_Selection_Logic.md) (1 shared connections)
- [Zim Schedules](Zim_Schedules.md) (1 shared connections)
- [Job Queues](Job_Queues.md) (1 shared connections)
- [Constants & Utilities](Constants_%26_Utilities.md) (1 shared connections)

## Source Files

- `wp1/logic/zim_schedules.py`
- `wp1/logic/zim_schedules_active_test.py`

## Audit Trail

- EXTRACTED: 92 (98%)
- INFERRED: 2 (2%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
