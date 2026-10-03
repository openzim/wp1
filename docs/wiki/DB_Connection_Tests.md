# DB Connection Tests

> 16 nodes

## Key Concepts

- **connect()** (13 connections) — `wp1/db.py`
- **DbTest** (7 connections) — `wp1/db_test.py`
- **db_test.py** (4 connections) — `wp1/db_test.py`
- **patch** (4 connections)
- **wikilang_db.py** (4 connections) — `wp1/wikilang_db.py`
- **.test_exception_thrown_with_empty_creds()** (3 connections) — `wp1/db_test.py`
- **.test_retries_four_times_failure()** (3 connections) — `wp1/db_test.py`
- **.test_socks_proxy()** (3 connections) — `wp1/db_test.py`
- **.test_socks_proxy_not_used()** (3 connections) — `wp1/db_test.py`
- **.test_connect_works()** (2 connections) — `wp1/db_test.py`
- **connect()** (2 connections) — `wp1/wikilang_db.py`
- **wikilang_db_test.py** (2 connections) — `wp1/wikilang_db_test.py`
- **WikiLangDbTest** (2 connections) — `wp1/wikilang_db_test.py`
- **.test_connect()** (2 connections) — `wp1/wikilang_db_test.py`
- **Connection** (1 connections)
- **patch** (1 connections)

## Relationships

- [Environment & Credentials Config](Environment_%26_Credentials_Config.md) (6 shared connections)
- [Init Test](Init_Test.md) (1 shared connections)
- [MediaWiki API Client](MediaWiki_API_Client.md) (1 shared connections)

## Source Files

- `wp1/db.py`
- `wp1/db_test.py`
- `wp1/wikilang_db.py`
- `wp1/wikilang_db_test.py`

## Audit Trail

- EXTRACTED: 55 (98%)
- INFERRED: 1 (2%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
