# ZimFarmTest

> God node · 96 connections · `wp1/zimfarm_test.py`

**Community:** [Zimfarm Client Tests](Zimfarm_Client_Tests.md)

## Connections by Relation

### contains

- zimfarm_test.py `EXTRACTED`

### method

- .\_insert_zim_schedule() `EXTRACTED`
- .setUp() `EXTRACTED`
- .test_create_or_update_zimfarm_schedule_updates() `EXTRACTED`
- .test_token_provider_generate_oauth_access_token_success() `EXTRACTED`
- .test_token_provider_get_access_token_expired_local() `EXTRACTED`
- .test_zimfarm_schedule_exists_no_token() `EXTRACTED`
- .\_insert_selection() `EXTRACTED`
- .test_create_or_update_zimfarm_schedule_create_empty_long_desc_ok() `EXTRACTED`
- .test_create_or_update_zimfarm_schedule_create_missing_long_desc_ok() `EXTRACTED`
- .test_create_or_update_zimfarm_schedule_creates() `EXTRACTED`
- .test_create_or_update_zimfarm_schedule_missing_token() `EXTRACTED`
- .test_delete_zimfarm_schedule_by_builder_id_no_token() `EXTRACTED`
- .test_find_existing_schedule_in_db_no_matching_schedule() `EXTRACTED`
- .test_find_existing_schedule_in_db_with_scheduled_repetitions() `EXTRACTED`
- .test_find_existing_schedule_in_db_without_scheduled_repetitions() `EXTRACTED`
- .test_request_zimfarm_task_missing_token() `EXTRACTED`
- .test_token_provider_generate_local_access_token_http_error() `EXTRACTED`
- .test_token_provider_generate_local_access_token_no_refresh() `EXTRACTED`
- .test_token_provider_generate_local_access_token_with_refresh() `EXTRACTED`
- .test_token_provider_generate_oauth_access_token_http_error() `EXTRACTED`

### uses

- [BaseWpOneDbTest](BaseWpOneDbTest.md) `INFERRED`
- [Builder](Builder.md) `INFERRED`
- [Selection](Selection.md) `INFERRED`
- Environment `INFERRED`
- ZimfarmClientTokenProvider `INFERRED`
- ZimFarmError `INFERRED`
- ObjectNotFoundError `INFERRED`
- InvalidZimTitleError `INFERRED`
- ZimFarmTooManyArticlesError `INFERRED`
- InvalidZimDescriptionError `INFERRED`
- InvalidZimLongDescriptionError `INFERRED`
- InvalidZimFlavourError `INFERRED`

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
