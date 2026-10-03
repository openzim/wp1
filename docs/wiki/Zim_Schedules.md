# Zim Schedules

> 11 nodes

## Key Concepts

- **schedule_future_zimfile_generations()** (17 connections) — `wp1/logic/zim_schedules.py`
- **update_zim_schedule()** (7 connections) — `wp1/logic/zim_schedules.py`
- **has_email_been_confirmed()** (4 connections) — `wp1/logic/zim_schedules.py`
- **Redis** (3 connections)
- **generate_email_confirmation_token()** (3 connections) — `wp1/logic/zim_schedules.py`
- **Builder** (1 connections)
- **Any** (1 connections)
- **Updates a ZimSchedule record based on the model state. Returns True if updated.** (1 connections) — `wp1/logic/zim_schedules.py`
- **Checks if an email address has been previously confirmed in any zim_schedule.…** (1 connections) — `wp1/logic/zim_schedules.py`
- **Generates a secure random token for email confirmation.** (1 connections) — `wp1/logic/zim_schedules.py`
- **Calculate timing and schedule future ZIM file creations using rq-scheduler,…** (1 connections) — `wp1/logic/zim_schedules.py`

## Relationships

- [ZIM Schedules & Emails](ZIM_Schedules_%26_Emails.md) (8 shared connections)
- [ZIM Schedule Logic](ZIM_Schedule_Logic.md) (8 shared connections)
- [Zimfarm Integration](Zimfarm_Integration.md) (1 shared connections)
- [Active Schedule Tests](Active_Schedule_Tests.md) (1 shared connections)
- [Builder & Selection Logic](Builder_%26_Selection_Logic.md) (1 shared connections)
- [Job Queues](Job_Queues.md) (1 shared connections)

## Source Files

- `wp1/logic/zim_schedules.py`

## Audit Trail

- EXTRACTED: 40 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
