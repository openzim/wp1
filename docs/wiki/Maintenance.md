# Maintenance

> 15 nodes

## Key Concepts

- **maintenance.py** (23 connections) — `wp1/maintenance.py`
- **enqueue_all()** (6 connections) — `wp1/maintenance.py`
- **update_global_articles()** (6 connections) — `wp1/maintenance.py`
- **rebuild_global_articles()** (6 connections) — `wp1/maintenance.py`
- **\_stop_inflight_update_jobs()** (5 connections) — `wp1/maintenance.py`
- **\_restart_upload_workers()** (4 connections) — `wp1/maintenance.py`
- **\_supervisorctl()** (3 connections) — `wp1/maintenance.py`
- **update_global_articles_for_project_name()** (2 connections) — `wp1/logic/project.py`
- **Redis** (2 connections)
- **Recurring maintenance jobs for the workers container. These replace the shell…** (1 connections) — `wp1/maintenance.py`
- **Nightly (midnight UTC): enqueue update + upload jobs for all projects.** (1 connections) — `wp1/maintenance.py`
- **Daily (04:00 UTC): rebuild the global articles table. The rebuild needs the…** (1 connections) — `wp1/maintenance.py`
- **Update the global articles table for every project, with no locking. Callers…** (1 connections) — `wp1/maintenance.py`
- **Tell the workers to kill any currently-executing update jobs.** (1 connections) — `wp1/maintenance.py`
- **Bounce the upload workers, as cron/enqueue-all.sh did before the nightly…** (1 connections) — `wp1/maintenance.py`

## Relationships

- [Environment & Credentials Config](Environment_%26_Credentials_Config.md) (5 shared connections)
- [20220818 01 5X0T9 Add Object](20220818_01_5X0T9_Add_Object.md) (4 shared connections)
- [Project & Rating Updates](Project_%26_Rating_Updates.md) (3 shared connections)
- [MediaWiki API Client](MediaWiki_API_Client.md) (3 shared connections)
- [Maintenance Tests](Maintenance_Tests.md) (2 shared connections)
- [Job Queues](Job_Queues.md) (2 shared connections)
- [Constants & Utilities](Constants_%26_Utilities.md) (1 shared connections)
- [Tables](Tables.md) (1 shared connections)
- [Init Test](Init_Test.md) (1 shared connections)
- [DB Test Harness](DB_Test_Harness.md) (1 shared connections)

## Source Files

- `wp1/logic/project.py`
- `wp1/maintenance.py`

## Audit Trail

- EXTRACTED: 62 (98%)
- INFERRED: 1 (2%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
