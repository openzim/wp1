# Builder & Selection Logic

> 87 nodes

## Key Concepts

- **logic/builder.py** (88 connections) — `wp1/logic/builder.py`
- **logic/selection.py** (28 connections) — `wp1/logic/selection.py`
- **Connection** (27 connections)
- **logic/builder_test.py** (20 connections) — `wp1/logic/builder_test.py`
- **Any** (18 connections)
- **materialize_builder()** (18 connections) — `wp1/logic/builder.py`
- **ObjectNotFoundError** (17 connections) — `wp1/exceptions.py`
- **Builder** (16 connections)
- **delete_builder()** (14 connections) — `wp1/logic/builder.py`
- **handle_zim_generation()** (13 connections) — `wp1/logic/builder.py`
- **request_zim_file_task_for_builder()** (12 connections) — `wp1/logic/builder.py`
- **get_builder()** (11 connections) — `wp1/logic/builder.py`
- **request_scheduled_zim_file_for_builder()** (11 connections) — `wp1/logic/builder.py`
- **zim_file_status_for()** (11 connections) — `wp1/logic/builder.py`
- **\_find_referencing_combinators()** (10 connections) — `wp1/logic/builder.py`
- **\_delete_builder_and_assets()** (10 connections) — `wp1/logic/builder.py`
- **auto_handle_zim_generation()** (10 connections) — `wp1/logic/builder.py`
- **latest_selection_for()** (9 connections) — `wp1/logic/builder.py`
- **Wp1Error** (8 connections) — `wp1/exceptions.py`
- **UserNotAuthorizedError** (8 connections) — `wp1/exceptions.py`
- **create_or_update_builder()** (8 connections) — `wp1/logic/builder.py`
- **Redis** (8 connections)
- **get_builders_with_selections()** (8 connections) — `wp1/logic/builder.py`
- **BuilderDeleteConfirmationError** (7 connections) — `wp1/exceptions.py`
- **\_assert_builder_owner()** (7 connections) — `wp1/logic/builder.py`
- _... and 62 more nodes in this community_

## Relationships

- [Zimfarm Integration](Zimfarm_Integration.md) (18 shared connections)
- [Builders Web Endpoints](Builders_Web_Endpoints.md) (18 shared connections)
- [ZIM Schedules & Emails](ZIM_Schedules_%26_Emails.md) (17 shared connections)
- [Selection Builder Framework](Selection_Builder_Framework.md) (16 shared connections)
- [Selection & Meta Builder](Selection_%26_Meta_Builder.md) (10 shared connections)
- [20220818 01 5X0T9 Add Object](20220818_01_5X0T9_Add_Object.md) (9 shared connections)
- [Constants & Utilities](Constants_%26_Utilities.md) (8 shared connections)
- [Builder Model & Errors](Builder_Model_%26_Errors.md) (7 shared connections)
- [ZIM Task Tracking](ZIM_Task_Tracking.md) (7 shared connections)
- [Storage Test](Storage_Test.md) (7 shared connections)
- [Environment & Credentials Config](Environment_%26_Credentials_Config.md) (6 shared connections)
- [Builder Logic Tests](Builder_Logic_Tests.md) (4 shared connections)

## Source Files

- `db/migrations/20220818_01_5x0T9-add-object-key-column-to-selections.py`
- `wp1/exceptions.py`
- `wp1/logic/builder.py`
- `wp1/logic/builder_test.py`
- `wp1/logic/selection.py`
- `wp1/logic/util.py`

## Audit Trail

- EXTRACTED: 598 (99%)
- INFERRED: 6 (1%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
