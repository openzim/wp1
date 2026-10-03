# Zimfarm

> 6 nodes

## Key Concepts

- **\_get_params()** (9 connections) — `wp1/zimfarm.py`
- **get_zim_filename_prefix()** (6 connections) — `wp1/zimfarm.py`
- **get_resource_profile()** (3 connections) — `wp1/logic/selection.py`
- **get_webhook_url()** (2 connections) — `wp1/zimfarm.py`
- **Builder** (2 connections)
- **Generate a filename prefix for the ZIM file based on builder and selection.** (1 connections) — `wp1/zimfarm.py`

## Relationships

- [Zimfarm Integration](Zimfarm_Integration.md) (5 shared connections)
- [Builder & Selection Logic](Builder_%26_Selection_Logic.md) (3 shared connections)
- [Selection & Meta Builder](Selection_%26_Meta_Builder.md) (3 shared connections)

## Source Files

- `wp1/logic/selection.py`
- `wp1/zimfarm.py`

## Audit Trail

- EXTRACTED: 23 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
