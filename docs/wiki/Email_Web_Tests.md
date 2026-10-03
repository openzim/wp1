# Email Web Tests

> 19 nodes

## Key Concepts

- **EmailsTest** (15 connections) — `wp1/web/emails_test.py`
- **patch** (10 connections)
- **.setUp()** (4 connections) — `wp1/web/emails_test.py`
- **.test_send_zim_ready_email()** (4 connections) — `wp1/web/emails_test.py`
- **.test_send_zim_ready_email_with_defaults()** (4 connections) — `wp1/web/emails_test.py`
- **.test_send_zim_ready_email_no_mailgun_config()** (4 connections) — `wp1/web/emails_test.py`
- **.test_send_zim_ready_email_no_api_key()** (4 connections) — `wp1/web/emails_test.py`
- **.test_send_zim_ready_email_api_error()** (4 connections) — `wp1/web/emails_test.py`
- **.test_send_zim_ready_email_request_exception()** (4 connections) — `wp1/web/emails_test.py`
- **.test_respond_to_zim_task_completed()** (4 connections) — `wp1/web/emails_test.py`
- **.test_respond_to_zim_task_completed_includes_unsubscribe_url()** (4 connections) — `wp1/web/emails_test.py`
- **Test successful email sending.** (1 connections) — `wp1/web/emails_test.py`
- **Test email sending with default URLs.** (1 connections) — `wp1/web/emails_test.py`
- **Test email sending when Mailgun is not configured.** (1 connections) — `wp1/web/emails_test.py`
- **Test email sending when API key is missing.** (1 connections) — `wp1/web/emails_test.py`
- **Test email sending when API returns an error.** (1 connections) — `wp1/web/emails_test.py`
- **Test email sending when request raises an exception.** (1 connections) — `wp1/web/emails_test.py`
- **Test successful user notification for scheduled ZIM.** (1 connections) — `wp1/web/emails_test.py`
- **Test that notification emails include unsubscribe URL.** (1 connections) — `wp1/web/emails_test.py`

## Relationships

- [ZIM Schedules & Emails](ZIM_Schedules_%26_Emails.md) (16 shared connections)
- [ZIM Task Tracking](ZIM_Task_Tracking.md) (2 shared connections)
- [DB Test Harness](DB_Test_Harness.md) (1 shared connections)

## Source Files

- `wp1/web/emails_test.py`

## Audit Trail

- EXTRACTED: 66 (96%)
- INFERRED: 3 (4%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
