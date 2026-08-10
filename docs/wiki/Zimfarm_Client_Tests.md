# Zimfarm Client Tests

> 76 nodes

## Key Concepts

- **ZimFarmTest** (96 connections) — `wp1/zimfarm_test.py`
- **patch** (57 connections)
- **ZimfarmClientTokenProvider** (35 connections) — `wp1/zimfarm.py`
- **.setUp()** (4 connections) — `wp1/zimfarm_test.py`
- **.test_token_provider_generate_oauth_access_token_success()** (4 connections) — `wp1/zimfarm_test.py`
- **.test_token_provider_get_access_token_expired_local()** (4 connections) — `wp1/zimfarm_test.py`
- **.\_insert_selection()** (3 connections) — `wp1/zimfarm_test.py`
- **.test_token_provider_init_oauth_valid()** (3 connections) — `wp1/zimfarm_test.py`
- **.test_token_provider_init_local_valid()** (3 connections) — `wp1/zimfarm_test.py`
- **.test_token_provider_init_oauth_missing_credentials()** (3 connections) — `wp1/zimfarm_test.py`
- **.test_token_provider_init_local_missing_credentials()** (3 connections) — `wp1/zimfarm_test.py`
- **.test_token_provider_init_unknown_auth_mode()** (3 connections) — `wp1/zimfarm_test.py`
- **.test_token_provider_generate_oauth_access_token_http_error()** (3 connections) — `wp1/zimfarm_test.py`
- **.test_token_provider_generate_local_access_token_no_refresh()** (3 connections) — `wp1/zimfarm_test.py`
- **.test_token_provider_generate_local_access_token_with_refresh()** (3 connections) — `wp1/zimfarm_test.py`
- **.test_token_provider_generate_local_access_token_http_error()** (3 connections) — `wp1/zimfarm_test.py`
- **.test_token_provider_get_access_token_not_expired()** (3 connections) — `wp1/zimfarm_test.py`
- **.test_token_provider_get_access_token_expired_oauth()** (3 connections) — `wp1/zimfarm_test.py`
- **.test_token_provider_get_access_token_no_redis_data_oauth()** (3 connections) — `wp1/zimfarm_test.py`
- **.test_token_provider_get_access_token_no_redis_data_local()** (3 connections) — `wp1/zimfarm_test.py`
- **.test_token_provider_get_access_token_stores_in_redis()** (3 connections) — `wp1/zimfarm_test.py`
- **.\_insert_builder()** (2 connections) — `wp1/zimfarm_test.py`
- **.test_create_or_update_zimfarm_schedule_missing_builder()** (2 connections) — `wp1/zimfarm_test.py`
- **.test_create_or_update_zimfarm_schedule_http_error()** (2 connections) — `wp1/zimfarm_test.py`
- **.test_create_or_update_zimfarm_schedule_too_long_title()** (2 connections) — `wp1/zimfarm_test.py`
- _... and 51 more nodes in this community_

## Relationships

- [Zimfarm Integration](Zimfarm_Integration.md) (25 shared connections)
- [Zimfarm Test](Zimfarm_Test.md) (20 shared connections)
- [Builder Model & Errors](Builder_Model_%26_Errors.md) (3 shared connections)
- [Selection & Meta Builder](Selection_%26_Meta_Builder.md) (3 shared connections)
- [Builder & Selection Logic](Builder_%26_Selection_Logic.md) (2 shared connections)
- [ZIM Schedules & Emails](ZIM_Schedules_%26_Emails.md) (1 shared connections)
- [DB Test Harness](DB_Test_Harness.md) (1 shared connections)
- [Environment & Credentials Config](Environment_%26_Credentials_Config.md) (1 shared connections)

## Source Files

- `wp1/zimfarm.py`
- `wp1/zimfarm_test.py`

## Audit Trail

- EXTRACTED: 309 (93%)
- INFERRED: 23 (7%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
