# ZIM Email Endpoints

> 17 nodes

## Key Concepts

- **app.py** (27 connections) — `wp1/web/app.py`
- **web/db.py** (11 connections) — `wp1/web/db.py`
- **web/selection.py** (9 connections) — `wp1/web/selection.py`
- **zim_emails.py** (8 connections) — `wp1/web/zim_emails.py`
- **confirm_email()** (7 connections) — `wp1/web/zim_emails.py`
- **unsubscribe_notification()** (7 connections) — `wp1/web/zim_emails.py`
- **unsubscribe_email()** (6 connections) — `wp1/web/zim_emails.py`
- **render_error_page()** (5 connections) — `wp1/web/zim_emails.py`
- **has_db()** (4 connections) — `wp1/web/db.py`
- **route** (3 connections)
- **get_redis_creds()** (2 connections) — `wp1/web/app.py`
- **get_secret_key()** (2 connections) — `wp1/web/app.py`
- **nocache()** (1 connections) — `wp1/web/app.py`
- **Renders a standardized error/success page using the shared template.** (1 connections) — `wp1/web/zim_emails.py`
- **Confirms email subscription for ZIM notifications.** (1 connections) — `wp1/web/zim_emails.py`
- **Unsubscribes from email notifications for ZIM files.** (1 connections) — `wp1/web/zim_emails.py`
- **Unsubscribes from email notifications for ZIM files using schedule ID.** (1 connections) — `wp1/web/zim_emails.py`

## Relationships

- [Builders Web Endpoints](Builders_Web_Endpoints.md) (12 shared connections)
- [Flask App Tests](Flask_App_Tests.md) (6 shared connections)
- [Environment & Credentials Config](Environment_%26_Credentials_Config.md) (4 shared connections)
- [OAuth Web Tests](OAuth_Web_Tests.md) (4 shared connections)
- [ZIM Schedules & Emails](ZIM_Schedules_%26_Emails.md) (4 shared connections)
- [Dev Project Stubs](Dev_Project_Stubs.md) (3 shared connections)
- [ZIM Schedule Logic](ZIM_Schedule_Logic.md) (3 shared connections)
- [MediaWiki API Client](MediaWiki_API_Client.md) (2 shared connections)
- [OAuth Endpoints](OAuth_Endpoints.md) (2 shared connections)
- [Projects Web Endpoints](Projects_Web_Endpoints.md) (2 shared connections)
- [Storage Test](Storage_Test.md) (2 shared connections)
- [Project & Rating Updates](Project_%26_Rating_Updates.md) (1 shared connections)

## Source Files

- `wp1/web/app.py`
- `wp1/web/db.py`
- `wp1/web/selection.py`
- `wp1/web/zim_emails.py`

## Audit Trail

- EXTRACTED: 96 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
