# ZimSchedule

> God node · 71 connections · `wp1/models/wp10/zim_schedule.py`

**Community:** [ZIM Schedules & Emails](ZIM_Schedules_%26_Emails.md)

## Connections by Relation

### calls

- create_or_update_zimfarm_schedule() `EXTRACTED`
- .new_schedule() `EXTRACTED`
- .test_handle_zim_generation_with_existing_schedule_update() `EXTRACTED`
- .new_schedule() `EXTRACTED`
- .\_create_active_schedule() `EXTRACTED`
- .test_create_zim_file_for_builder_scheduled_repetitions() `EXTRACTED`
- .test_create_zim_file_for_builder_scheduled_repetitions_extra_fields() `EXTRACTED`
- .test_handle_zim_generation_create_new_schedule() `EXTRACTED`
- .test_schedule_future_zimfile_generations_with_email_sends_confirmation() `EXTRACTED`
- .test_schedule_future_zimfile_generations_without_email_no_token() `EXTRACTED`
- .test_schedule_with_previously_confirmed_email_skips_confirmation() `EXTRACTED`
- .test_create_zim_file_for_builder() `EXTRACTED`
- .test_create_zim_file_for_builder_scheduled_repetitions_empty_dict() `EXTRACTED`
- .test_create_zim_file_for_builder_with_flavour() `EXTRACTED`
- .test_respond_to_zim_task_completed_with_confirmed_email() `EXTRACTED`
- .test_respond_to_zim_task_completed_with_no_email() `EXTRACTED`
- .test_respond_to_zim_task_completed_with_unconfirmed_email() `EXTRACTED`
- .test_respond_to_zim_task_completed_no_remaining_generations() `EXTRACTED`
- .test_respond_to_zim_task_completed_no_title() `EXTRACTED`
- .test_handle_zim_generation() `EXTRACTED`

### contains

- zim_schedule.py `EXTRACTED`

### imports

- logic/builder.py `EXTRACTED`
- zimfarm.py `EXTRACTED`
- queues.py `EXTRACTED`
- zim_schedules.py `EXTRACTED`
- logic/builder_test.py `EXTRACTED`
- builders_schedule_test.py `EXTRACTED`
- emails_confirmation_test.py `EXTRACTED`
- zim_schedules_active_test.py `EXTRACTED`
- emails.py `EXTRACTED`
- emails_test.py `EXTRACTED`
- builders_test.py `EXTRACTED`
- zim_schedules_test.py `EXTRACTED`
- zim_emails_test.py `EXTRACTED`
- zim_schedules_email_test.py `EXTRACTED`
- zim_schedule_test.py `EXTRACTED`

### method

- .set_last_updated_at_dt() `EXTRACTED`
- .set_last_updated_at_now() `EXTRACTED`
- .last_updated_at_dt() `EXTRACTED`
- .set_id() `EXTRACTED`

### references

- insert_zim_schedule() `EXTRACTED`
- get_zim_schedule() `EXTRACTED`
- respond_to_zim_task_completed() `EXTRACTED`
- find_active_recurring_schedule_for_builder() `EXTRACTED`
- notify_user_for_scheduled_zim() `EXTRACTED`
- update_zim_schedule() `EXTRACTED`
- get_zim_schedule_by_zim_file_id() `EXTRACTED`
- list_zim_schedules_for_builder() `EXTRACTED`
- get_scheduled_zimfarm_task_from_taskid() `EXTRACTED`
- get_zim_schedule_by_token() `EXTRACTED`
- \_format_active_schedule_data() `EXTRACTED`
- s `EXTRACTED`

### uses

- [BuilderTest](BuilderTest.md) `INFERRED`
- [BuildersTest](BuildersTest.md) `INFERRED`
- ZimfarmClientTokenProvider `INFERRED`
- LogicZimSchedulesTest `INFERRED`
- ZimSchedulesEmailConfirmationTest `INFERRED`
- ZimEmailsEndpointsTest `INFERRED`
- EmailsTest `INFERRED`
- BuildersScheduleTest `INFERRED`
- EmailConfirmationTest `INFERRED`
- LogicZimSchedulesActiveTest `INFERRED`
- ModelsZimScheduleTest `INFERRED`

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
