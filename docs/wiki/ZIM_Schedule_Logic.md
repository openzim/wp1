# ZIM Schedule Logic

> 49 nodes

## Key Concepts

- **insert_zim_schedule()** (28 connections) — `wp1/logic/zim_schedules.py`
- **LogicZimSchedulesTest** (25 connections) — `wp1/logic/zim_schedules_test.py`
- **.new_schedule()** (19 connections) — `wp1/logic/zim_schedules_test.py`
- **get_zim_schedule()** (18 connections) — `wp1/logic/zim_schedules.py`
- **Connection** (17 connections)
- **decrement_remaining_generations()** (8 connections) — `wp1/logic/zim_schedules.py`
- **get_username_by_zim_schedule_id()** (8 connections) — `wp1/logic/zim_schedules.py`
- **get_zim_schedule_by_zim_file_id()** (7 connections) — `wp1/logic/zim_schedules.py`
- **list_zim_schedules_for_builder()** (7 connections) — `wp1/logic/zim_schedules.py`
- **unsubscribe_email_by_schedule_id()** (7 connections) — `wp1/logic/zim_schedules.py`
- **get_scheduled_zimfarm_task_from_taskid()** (6 connections) — `wp1/logic/zim_schedules.py`
- **set_zim_schedule_id_to_zim_task_by_selection()** (6 connections) — `wp1/logic/zim_schedules.py`
- **.test_update_schedule()** (6 connections) — `wp1/logic/zim_schedules_test.py`
- **.test_schedule_future_zimfile_generations()** (6 connections) — `wp1/logic/zim_schedules_test.py`
- **.test_unsubscribe_email_by_schedule_id_success()** (6 connections) — `wp1/logic/zim_schedules_test.py`
- **.test_decrement_remaining_generations()** (5 connections) — `wp1/logic/zim_schedules_test.py`
- **.test_decrement_remaining_generations_from_0()** (5 connections) — `wp1/logic/zim_schedules_test.py`
- **.test_decrement_remaining_generations_from_minus_1()** (5 connections) — `wp1/logic/zim_schedules_test.py`
- **.test_schedule_future_zimfile_generations_missing_fields()** (5 connections) — `wp1/logic/zim_schedules_test.py`
- **.test_unsubscribe_email_by_schedule_id_no_email()** (5 connections) — `wp1/logic/zim_schedules_test.py`
- **confirm_email_subscription()** (4 connections) — `wp1/logic/zim_schedules.py`
- **.test_insert_and_get()** (4 connections) — `wp1/logic/zim_schedules_test.py`
- **.test_list_for_builder()** (4 connections) — `wp1/logic/zim_schedules_test.py`
- **.test_get_scheduled_zimfarm_task_from_taskid()** (4 connections) — `wp1/logic/zim_schedules_test.py`
- **.test_get_scheduled_zimfarm_task_from_taskid_is_none()** (4 connections) — `wp1/logic/zim_schedules_test.py`
- _... and 24 more nodes in this community_

## Relationships

- [ZIM Schedules & Emails](ZIM_Schedules_%26_Emails.md) (26 shared connections)
- [Active Schedule Tests](Active_Schedule_Tests.md) (12 shared connections)
- [Zim Schedules](Zim_Schedules.md) (8 shared connections)
- [Zimfarm Integration](Zimfarm_Integration.md) (3 shared connections)
- [ZIM Email Endpoints](ZIM_Email_Endpoints.md) (3 shared connections)
- [Builder Model & Errors](Builder_Model_%26_Errors.md) (3 shared connections)
- [Builder & Selection Logic](Builder_%26_Selection_Logic.md) (2 shared connections)
- [Builders Schedule Test](Builders_Schedule_Test.md) (1 shared connections)
- [Builders Web Endpoints](Builders_Web_Endpoints.md) (1 shared connections)
- [DB Test Harness](DB_Test_Harness.md) (1 shared connections)

## Source Files

- `wp1/logic/zim_schedules.py`
- `wp1/logic/zim_schedules_test.py`

## Audit Trail

- EXTRACTED: 259 (99%)
- INFERRED: 3 (1%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
