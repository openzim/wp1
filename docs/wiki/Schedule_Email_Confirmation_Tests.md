# Schedule Email Confirmation Tests

> 34 nodes

## Key Concepts

- **ZimSchedulesEmailConfirmationTest** (20 connections) — `wp1/logic/zim_schedules_email_test.py`
- **.\_insert_zim_schedule_directly()** (12 connections) — `wp1/logic/zim_schedules_email_test.py`
- **.test_schedule_future_zimfile_generations_with_email_sends_confirmation()** (6 connections) — `wp1/logic/zim_schedules_email_test.py`
- **.test_schedule_future_zimfile_generations_without_email_no_token()** (6 connections) — `wp1/logic/zim_schedules_email_test.py`
- **.test_schedule_with_previously_confirmed_email_skips_confirmation()** (6 connections) — `wp1/logic/zim_schedules_email_test.py`
- **.test_has_email_been_confirmed_true_confirmed_email()** (5 connections) — `wp1/logic/zim_schedules_email_test.py`
- **.test_insert_zim_schedule_with_token()** (3 connections) — `wp1/logic/zim_schedules_email_test.py`
- **.test_get_zim_schedule_by_token()** (3 connections) — `wp1/logic/zim_schedules_email_test.py`
- **.test_confirm_email_subscription()** (3 connections) — `wp1/logic/zim_schedules_email_test.py`
- **.test_unsubscribe_email()** (3 connections) — `wp1/logic/zim_schedules_email_test.py`
- **patch** (3 connections)
- **.test_has_email_been_confirmed_false_unconfirmed_email()** (3 connections) — `wp1/logic/zim_schedules_email_test.py`
- **.test_confirm_email_subscription_confirms_all_with_same_email()** (3 connections) — `wp1/logic/zim_schedules_email_test.py`
- **.test_generate_email_confirmation_token()** (2 connections) — `wp1/logic/zim_schedules_email_test.py`
- **.test_get_zim_schedule_by_token_not_found()** (2 connections) — `wp1/logic/zim_schedules_email_test.py`
- **.test_confirm_email_subscription_invalid_token()** (2 connections) — `wp1/logic/zim_schedules_email_test.py`
- **.test_unsubscribe_email_invalid_token()** (2 connections) — `wp1/logic/zim_schedules_email_test.py`
- **.test_has_email_been_confirmed_false_no_email()** (2 connections) — `wp1/logic/zim_schedules_email_test.py`
- **Helper method to insert a ZimSchedule directly into the database without using…** (1 connections) — `wp1/logic/zim_schedules_email_test.py`
- **Test that a token is generated and is valid.** (1 connections) — `wp1/logic/zim_schedules_email_test.py`
- **Test inserting a schedule with email confirmation token.** (1 connections) — `wp1/logic/zim_schedules_email_test.py`
- **Test retrieving a schedule by its confirmation token.** (1 connections) — `wp1/logic/zim_schedules_email_test.py`
- **Test retrieving a schedule by non-existent token.** (1 connections) — `wp1/logic/zim_schedules_email_test.py`
- **Test confirming email subscription by removing token.** (1 connections) — `wp1/logic/zim_schedules_email_test.py`
- **Test confirming with invalid token.** (1 connections) — `wp1/logic/zim_schedules_email_test.py`
- _... and 9 more nodes in this community_

## Relationships

- [ZIM Schedules & Emails](ZIM_Schedules_%26_Emails.md) (11 shared connections)
- [DB Test Harness](DB_Test_Harness.md) (1 shared connections)

## Source Files

- `wp1/logic/zim_schedules_email_test.py`

## Audit Trail

- EXTRACTED: 100 (98%)
- INFERRED: 2 (2%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
