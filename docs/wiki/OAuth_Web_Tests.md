# OAuth Web Tests

> 32 nodes

## Key Concepts

- **create_app()** (105 connections) — `wp1/web/app.py`
- **patch** (22 connections)
- **IdentifyTest** (18 connections) — `wp1/web/oauth_test.py`
- **.test_complete_authorized_user_with_next_path()** (4 connections) — `wp1/web/oauth_test.py`
- **.test_initiate_dev_mode_no_creds_redirects_to_homepage()** (4 connections) — `wp1/web/oauth_test.py`
- **.test_initiate_dev_mode_no_creds_with_next_path()** (4 connections) — `wp1/web/oauth_test.py`
- **.test_initiate_dev_mode_no_creds_sets_session()** (4 connections) — `wp1/web/oauth_test.py`
- **.test_initiate_dev_mode_idempotency()** (4 connections) — `wp1/web/oauth_test.py`
- **.test_initiate_dev_mode_multiple_sessions_same_user()** (4 connections) — `wp1/web/oauth_test.py`
- **.test_initiate_dev_mode_with_creds_redirects_to_oauth()** (4 connections) — `wp1/web/oauth_test.py`
- **.test_initiate_dev_mode_with_creds_does_not_create_fake_user()** (4 connections) — `wp1/web/oauth_test.py`
- **.test_initiate_authorized_user()** (3 connections) — `wp1/web/oauth_test.py`
- **.test_initiate_unauthorized_user()** (3 connections) — `wp1/web/oauth_test.py`
- **.test_initiate_authorized_user_with_next_path()** (3 connections) — `wp1/web/oauth_test.py`
- **.test_complete_unauthorized_user()** (3 connections) — `wp1/web/oauth_test.py`
- **.test_complete_authorized_user_email()** (3 connections) — `wp1/web/oauth_test.py`
- **.test_complete_authorized_user()** (3 connections) — `wp1/web/oauth_test.py`
- **.test_identify_authorized_user()** (3 connections) — `wp1/web/oauth_test.py`
- **.test_identify_unauthorized_user()** (3 connections) — `wp1/web/oauth_test.py`
- **.test_logout_authorized_user()** (3 connections) — `wp1/web/oauth_test.py`
- **.test_logout_unauthorized_user()** (3 connections) — `wp1/web/oauth_test.py`
- **.test_email_unauthorized_user()** (3 connections) — `wp1/web/oauth_test.py`
- **.test_email_authorized_user_with_email_in_session()** (3 connections) — `wp1/web/oauth_test.py`
- **.test_email_authorized_user_without_session_exists_in_db()** (3 connections) — `wp1/web/oauth_test.py`
- **.test_email_authorized_user_without_session_not_in_db()** (3 connections) — `wp1/web/oauth_test.py`
- _... and 7 more nodes in this community_

## Relationships

- [Builders API Tests](Builders_API_Tests.md) (57 shared connections)
- [Flask App Tests](Flask_App_Tests.md) (10 shared connections)
- [Environment & Credentials Config](Environment_%26_Credentials_Config.md) (10 shared connections)
- [Selection Test](Selection_Test.md) (5 shared connections)
- [ZIM Email Endpoints](ZIM_Email_Endpoints.md) (4 shared connections)
- [Builders Test](Builders_Test.md) (4 shared connections)
- [ZIM Schedules & Emails](ZIM_Schedules_%26_Emails.md) (2 shared connections)
- [Projects Web Endpoints](Projects_Web_Endpoints.md) (1 shared connections)
- [Builders Web Endpoints](Builders_Web_Endpoints.md) (1 shared connections)

## Source Files

- `wp1/web/app.py`
- `wp1/web/oauth_test.py`

## Audit Trail

- EXTRACTED: 223 (99%)
- INFERRED: 3 (1%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
