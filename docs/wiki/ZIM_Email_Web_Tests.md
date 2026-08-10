# ZIM Email Web Tests

> 23 nodes

## Key Concepts

- **ZimEmailsEndpointsTest** (16 connections) — `wp1/web/zim_emails_test.py`
- **.test_unsubscribe_notification_no_email()** (4 connections) — `wp1/web/zim_emails_test.py`
- **.test_confirm_email_success()** (2 connections) — `wp1/web/zim_emails_test.py`
- **.test_confirm_email_missing_token()** (2 connections) — `wp1/web/zim_emails_test.py`
- **.test_confirm_email_invalid_token()** (2 connections) — `wp1/web/zim_emails_test.py`
- **.test_confirm_email_already_confirmed()** (2 connections) — `wp1/web/zim_emails_test.py`
- **.test_unsubscribe_email_success()** (2 connections) — `wp1/web/zim_emails_test.py`
- **.test_unsubscribe_email_missing_token()** (2 connections) — `wp1/web/zim_emails_test.py`
- **.test_unsubscribe_email_invalid_token()** (2 connections) — `wp1/web/zim_emails_test.py`
- **.test_unsubscribe_email_already_unsubscribed()** (2 connections) — `wp1/web/zim_emails_test.py`
- **.test_unsubscribe_notification_missing_schedule_id()** (2 connections) — `wp1/web/zim_emails_test.py`
- **.test_unsubscribe_notification_invalid_schedule_id()** (2 connections) — `wp1/web/zim_emails_test.py`
- **Test successful email confirmation.** (1 connections) — `wp1/web/zim_emails_test.py`
- **Test email confirmation with missing token.** (1 connections) — `wp1/web/zim_emails_test.py`
- **Test email confirmation with invalid token.** (1 connections) — `wp1/web/zim_emails_test.py`
- **Test email confirmation with already used token.** (1 connections) — `wp1/web/zim_emails_test.py`
- **Test successful email unsubscribe.** (1 connections) — `wp1/web/zim_emails_test.py`
- **Test email unsubscribe with missing token.** (1 connections) — `wp1/web/zim_emails_test.py`
- **Test email unsubscribe with invalid token.** (1 connections) — `wp1/web/zim_emails_test.py`
- **Test email unsubscribe with already used token.** (1 connections) — `wp1/web/zim_emails_test.py`
- **Test notification unsubscribe without schedule_id parameter.** (1 connections) — `wp1/web/zim_emails_test.py`
- **Test notification unsubscribe with invalid schedule ID.** (1 connections) — `wp1/web/zim_emails_test.py`
- **Test notification unsubscribe for schedule without email.** (1 connections) — `wp1/web/zim_emails_test.py`

## Relationships

- [ZIM Schedules & Emails](ZIM_Schedules_%26_Emails.md) (6 shared connections)
- [DB Test Harness](DB_Test_Harness.md) (1 shared connections)

## Source Files

- `wp1/web/zim_emails_test.py`

## Audit Trail

- EXTRACTED: 49 (96%)
- INFERRED: 2 (4%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
