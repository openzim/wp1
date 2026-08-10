# Api Test

> 15 nodes

## Key Concepts

- **patch** (8 connections)
- **ApiTest** (7 connections) — `wp1/api_test.py`
- **ApiWithCredsTest** (6 connections) — `wp1/api_test.py`
- **api_test.py** (3 connections) — `wp1/api_test.py`
- **.test_login()** (2 connections) — `wp1/api_test.py`
- **.test_login_already_logged_in()** (2 connections) — `wp1/api_test.py`
- **.test_login_exception()** (2 connections) — `wp1/api_test.py`
- **.test_login_corrupted_cookie_jar()** (2 connections) — `wp1/api_test.py`
- **.test_login_corrupted_cookie_jar_still_logs_in()** (2 connections) — `wp1/api_test.py`
- **.test_save_page()** (2 connections) — `wp1/api_test.py`
- **.test_save_page_tries_login_on_none_site()** (2 connections) — `wp1/api_test.py`
- **.test_save_page_no_credentials()** (2 connections) — `wp1/api_test.py`
- **.setUp()** (1 connections) — `wp1/api_test.py`
- **.test_get_revision_id_present()** (1 connections) — `wp1/api_test.py`
- **.test_get_revision_id_absent()** (1 connections) — `wp1/api_test.py`

## Relationships

- [MediaWiki API Client](MediaWiki_API_Client.md) (1 shared connections)

## Source Files

- `wp1/api_test.py`

## Audit Trail

- EXTRACTED: 43 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
