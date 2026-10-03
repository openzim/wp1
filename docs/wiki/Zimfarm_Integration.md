# Zimfarm Integration

> 42 nodes

## Key Concepts

- **zimfarm.py** (45 connections) — `wp1/zimfarm.py`
- **ZimFarmError** (32 connections) — `wp1/exceptions.py`
- **create_or_update_zimfarm_schedule()** (20 connections) — `wp1/zimfarm.py`
- **zimfarm_test.py** (19 connections) — `wp1/zimfarm_test.py`
- **.get_access_token()** (13 connections) — `wp1/zimfarm.py`
- **request_zimfarm_task()** (11 connections) — `wp1/zimfarm.py`
- **InvalidZimTitleError** (10 connections) — `wp1/exceptions.py`
- **ZimFarmTooManyArticlesError** (10 connections) — `wp1/exceptions.py`
- **get_zimfarm_url()** (10 connections) — `wp1/zimfarm.py`
- **InvalidZimDescriptionError** (8 connections) — `wp1/exceptions.py`
- **InvalidZimLongDescriptionError** (8 connections) — `wp1/exceptions.py`
- **InvalidZimFlavourError** (8 connections) — `wp1/exceptions.py`
- **zimfarm_schedule_exists()** (8 connections) — `wp1/zimfarm.py`
- **delete_zimfarm_schedule_by_builder_id()** (8 connections) — `wp1/zimfarm.py`
- **\_validate_zim_metadata()** (7 connections) — `wp1/zimfarm.py`
- **get_zimfarm_schedule_name()** (7 connections) — `wp1/zimfarm.py`
- **\_get_zimfarm_headers()** (6 connections) — `wp1/zimfarm.py`
- **cancel_zim_by_task_id()** (6 connections) — `wp1/zimfarm.py`
- **.\_generate_oauth_access_token()** (5 connections) — `wp1/zimfarm.py`
- **zim_file_url_for_task_id()** (5 connections) — `wp1/zimfarm.py`
- **naive_utcnow()** (4 connections) — `wp1/timestamp.py`
- **.\_generate_local_access_token()** (4 connections) — `wp1/zimfarm.py`
- **find_existing_schedule_in_db()** (4 connections) — `wp1/zimfarm.py`
- **validate_flavour()** (3 connections) — `wp1/zimfarm.py`
- **.\_validate_creds()** (3 connections) — `wp1/zimfarm.py`
- _... and 17 more nodes in this community_

## Relationships

- [Zimfarm Client Tests](Zimfarm_Client_Tests.md) (25 shared connections)
- [Builder & Selection Logic](Builder_%26_Selection_Logic.md) (18 shared connections)
- [Selection Builder Framework](Selection_Builder_Framework.md) (10 shared connections)
- [ZIM Schedules & Emails](ZIM_Schedules_%26_Emails.md) (8 shared connections)
- [Builders Web Endpoints](Builders_Web_Endpoints.md) (7 shared connections)
- [Zimfarm](Zimfarm.md) (5 shared connections)
- [Selection & Meta Builder](Selection_%26_Meta_Builder.md) (4 shared connections)
- [Environment & Credentials Config](Environment_%26_Credentials_Config.md) (3 shared connections)
- [ZIM Schedule Logic](ZIM_Schedule_Logic.md) (3 shared connections)
- [Builder Logic Tests](Builder_Logic_Tests.md) (2 shared connections)
- [Flask App Tests](Flask_App_Tests.md) (2 shared connections)
- [Constants & Utilities](Constants_%26_Utilities.md) (2 shared connections)

## Source Files

- `wp1/exceptions.py`
- `wp1/timestamp.py`
- `wp1/zimfarm.py`
- `wp1/zimfarm_test.py`

## Audit Trail

- EXTRACTED: 277 (95%)
- INFERRED: 15 (5%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
