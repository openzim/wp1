# Storage Test

> 12 nodes

## Key Concepts

- **connect_storage()** (14 connections) — `wp1/storage.py`
- **wp1/storage.py** (7 connections) — `wp1/storage.py`
- **StorageTest** (6 connections) — `wp1/storage_test.py`
- **wp1/storage_test.py** (5 connections) — `wp1/storage_test.py`
- **patch** (4 connections)
- **20250325_01_sFddz-add-article-count-to-selection-table.py** (3 connections) — `db/migrations/20250325_01_sFddz-add-article-count-to-selection-table.py`
- **.test_connect_storage_raises_if_no_credentials()** (3 connections) — `wp1/storage_test.py`
- **.test_connect_storage_raises_if_no_storage_key()** (3 connections) — `wp1/storage_test.py`
- **.test_connect_storage_connects_to_kiwixstorage()** (3 connections) — `wp1/storage_test.py`
- **.test_connect_storage_checks_permissions()** (3 connections) — `wp1/storage_test.py`
- **update_article_counts()** (2 connections) — `db/migrations/20250325_01_sFddz-add-article-count-to-selection-table.py`
- **Add article count to selection table** (1 connections) — `db/migrations/20250325_01_sFddz-add-article-count-to-selection-table.py`

## Relationships

- [Builder & Selection Logic](Builder_%26_Selection_Logic.md) (7 shared connections)
- [Environment & Credentials Config](Environment_%26_Credentials_Config.md) (4 shared connections)
- [Storage Test](Storage_Test.md) (3 shared connections)

## Source Files

- `db/migrations/20250325_01_sFddz-add-article-count-to-selection-table.py`
- `wp1/storage.py`
- `wp1/storage_test.py`

## Audit Trail

- EXTRACTED: 53 (98%)
- INFERRED: 1 (2%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
