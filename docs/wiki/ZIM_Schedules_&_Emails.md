# ZIM Schedules & Emails

> 56 nodes

## Key Concepts

- **ZimSchedule** (71 connections) — `wp1/models/wp10/zim_schedule.py`
- **utcnow()** (50 connections) — `wp1/timestamp.py`
- **zim_schedules.py** (40 connections) — `wp1/logic/zim_schedules.py`
- **zim_schedule.py** (20 connections) — `wp1/models/wp10/zim_schedule.py`
- **timestamp.py** (20 connections) — `wp1/timestamp.py`
- **respond_to_zim_task_completed()** (16 connections) — `wp1/web/emails.py`
- **zim_file.py** (14 connections) — `wp1/models/wp10/zim_file.py`
- **builders_schedule_test.py** (14 connections) — `wp1/web/builders_schedule_test.py`
- **emails_confirmation_test.py** (14 connections) — `wp1/web/emails_confirmation_test.py`
- **emails.py** (13 connections) — `wp1/web/emails.py`
- **emails_test.py** (13 connections) — `wp1/web/emails_test.py`
- **zim_schedules_test.py** (11 connections) — `wp1/logic/zim_schedules_test.py`
- **EmailConfirmationTest** (11 connections) — `wp1/web/emails_confirmation_test.py`
- **zim_emails_test.py** (11 connections) — `wp1/web/zim_emails_test.py`
- **send_zim_ready_email()** (10 connections) — `wp1/web/emails.py`
- **zim_schedules_email_test.py** (9 connections) — `wp1/logic/zim_schedules_email_test.py`
- **notify_user_for_scheduled_zim()** (8 connections) — `wp1/web/emails.py`
- **send_zim_email_confirmation()** (8 connections) — `wp1/web/emails_confirmation.py`
- **get_zim_schedule_by_token()** (6 connections) — `wp1/logic/zim_schedules.py`
- **patch** (6 connections)
- **.test_respond_to_zim_task_completed_with_unconfirmed_email()** (6 connections) — `wp1/web/emails_confirmation_test.py`
- **.test_respond_to_zim_task_completed_with_confirmed_email()** (6 connections) — `wp1/web/emails_confirmation_test.py`
- **.test_respond_to_zim_task_completed_with_no_email()** (6 connections) — `wp1/web/emails_confirmation_test.py`
- **.test_respond_to_zim_task_completed_no_remaining_generations()** (6 connections) — `wp1/web/emails_test.py`
- **.test_respond_to_zim_task_completed_no_title()** (6 connections) — `wp1/web/emails_test.py`
- _... and 31 more nodes in this community_

## Relationships

- [ZIM Schedule Logic](ZIM_Schedule_Logic.md) (26 shared connections)
- [Builder & Selection Logic](Builder_%26_Selection_Logic.md) (17 shared connections)
- [Email Web Tests](Email_Web_Tests.md) (16 shared connections)
- [DB Test Harness](DB_Test_Harness.md) (13 shared connections)
- [ZIM Task Tracking](ZIM_Task_Tracking.md) (13 shared connections)
- [Active Schedule Tests](Active_Schedule_Tests.md) (11 shared connections)
- [Schedule Email Confirmation Tests](Schedule_Email_Confirmation_Tests.md) (11 shared connections)
- [Constants & Utilities](Constants_%26_Utilities.md) (9 shared connections)
- [Zim Schedules](Zim_Schedules.md) (8 shared connections)
- [Zimfarm Integration](Zimfarm_Integration.md) (8 shared connections)
- [Job Queues](Job_Queues.md) (6 shared connections)
- [Builders API Tests](Builders_API_Tests.md) (6 shared connections)

## Source Files

- `wp1/logic/zim_schedules.py`
- `wp1/logic/zim_schedules_email_test.py`
- `wp1/logic/zim_schedules_test.py`
- `wp1/models/wp10/zim_file.py`
- `wp1/models/wp10/zim_schedule.py`
- `wp1/timestamp.py`
- `wp1/web/builders_schedule_test.py`
- `wp1/web/emails.py`
- `wp1/web/emails_confirmation.py`
- `wp1/web/emails_confirmation_test.py`
- `wp1/web/emails_test.py`
- `wp1/web/zim_emails_test.py`

## Audit Trail

- EXTRACTED: 443 (97%)
- INFERRED: 14 (3%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
