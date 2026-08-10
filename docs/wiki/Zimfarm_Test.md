# Zimfarm Test

> 9 nodes

## Key Concepts

- **.\_insert_zim_schedule()** (5 connections) — `wp1/zimfarm_test.py`
- **.test_create_or_update_zimfarm_schedule_updates()** (4 connections) — `wp1/zimfarm_test.py`
- **.test_find_existing_schedule_in_db_with_scheduled_repetitions()** (3 connections) — `wp1/zimfarm_test.py`
- **.test_find_existing_schedule_in_db_without_scheduled_repetitions()** (3 connections) — `wp1/zimfarm_test.py`
- **.test_find_existing_schedule_in_db_no_matching_schedule()** (3 connections) — `wp1/zimfarm_test.py`
- **Test that an existing schedule is updated and persisted in the DB.** (1 connections) — `wp1/zimfarm_test.py`
- **Test finding existing manual schedule when scheduled_repetitions is set.** (1 connections) — `wp1/zimfarm_test.py`
- **Test finding existing schedule with 0 remaining generations when…** (1 connections) — `wp1/zimfarm_test.py`
- **Test when no matching schedule exists.** (1 connections) — `wp1/zimfarm_test.py`

## Relationships

- [Zimfarm Client Tests](Zimfarm_Client_Tests.md) (6 shared connections)

## Source Files

- `wp1/zimfarm_test.py`

## Audit Trail

- EXTRACTED: 22 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
