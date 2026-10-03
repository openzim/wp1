# Storage Test

> 11 nodes

## Key Concepts

- **get_storage()** (9 connections) — `wp1/web/storage.py`
- **web/storage_test.py** (8 connections) — `wp1/web/storage_test.py`
- **StorageTest** (8 connections) — `wp1/web/storage_test.py`
- **web/storage.py** (7 connections) — `wp1/web/storage.py`
- **has_storage()** (5 connections) — `wp1/web/storage.py`
- **patch** (3 connections)
- **.test_get_storage_does_not_connect_if_existing()** (3 connections) — `wp1/web/storage_test.py`
- **.test_get_storage_sets_storage()** (3 connections) — `wp1/web/storage_test.py`
- **.test_get_storage_returns_s3()** (3 connections) — `wp1/web/storage_test.py`
- **.test_has_storage_empty()** (2 connections) — `wp1/web/storage_test.py`
- **.test_has_storage_exists()** (2 connections) — `wp1/web/storage_test.py`

## Relationships

- [Storage Test](Storage_Test.md) (3 shared connections)
- [Environment & Credentials Config](Environment_%26_Credentials_Config.md) (3 shared connections)
- [Flask App Tests](Flask_App_Tests.md) (3 shared connections)
- [Builders Web Endpoints](Builders_Web_Endpoints.md) (2 shared connections)
- [ZIM Email Endpoints](ZIM_Email_Endpoints.md) (2 shared connections)

## Source Files

- `wp1/web/storage.py`
- `wp1/web/storage_test.py`

## Audit Trail

- EXTRACTED: 51 (96%)
- INFERRED: 2 (4%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
