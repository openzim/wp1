# BuilderTest

> God node · 104 connections · `wp1/logic/builder_test.py`

**Community:** [Builder Logic Tests](Builder_Logic_Tests.md)

## Connections by Relation

### contains

- logic/builder_test.py `EXTRACTED`

### method

- .\_insert_builder() `EXTRACTED`
- .\_insert_selection() `EXTRACTED`
- .\_insert_zim_schedule() `EXTRACTED`
- .\_insert_builder_with_multiple_version_selections() `EXTRACTED`
- .\_insert_builder_record() `EXTRACTED`
- .\_get_builder_by_user_id() `EXTRACTED`
- .test_handle_zim_generation_with_existing_schedule_update() `EXTRACTED`
- .test_request_scheduled_zim_file_for_builder_with_zim_schedule() `EXTRACTED`
- .\_get_builder_params() `EXTRACTED`
- .test_handle_zim_generation_create_new_schedule() `EXTRACTED`
- .test_materialize_builder_no_update_zim_version() `EXTRACTED`
- .test_request_scheduled_zim_file_for_builder() `EXTRACTED`
- .test_request_scheduled_zim_file_for_builder_missing_class() `EXTRACTED`
- .test_request_zim_file_task_for_builder() `EXTRACTED`
- .\_setup_failed_zim_regeneration_scenario() `EXTRACTED`
- .test_auto_handle_zim_generation() `EXTRACTED`
- .test_auto_handle_zim_generation_cancel_tasks() `EXTRACTED`
- .test_auto_handle_zim_generation_with_flavour() `EXTRACTED`
- .test_auto_handle_zim_generation_zimfarm_error() `EXTRACTED`
- .test_delete_builder_retryable_selection_without_object_key() `EXTRACTED`

### uses

- [BaseWpOneDbTest](BaseWpOneDbTest.md) `INFERRED`
- [ZimSchedule](ZimSchedule.md) `INFERRED`
- [Builder](Builder.md) `INFERRED`
- Environment `INFERRED`
- ZimTask `INFERRED`
- ZimFarmError `INFERRED`
- ObjectNotFoundError `INFERRED`
- [Builder](Builder.md) `INFERRED`
- InvalidZimTitleError `INFERRED`
- UserNotAuthorizedError `INFERRED`
- BuilderDeleteConfirmationError `INFERRED`

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
