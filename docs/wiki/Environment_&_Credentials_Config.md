# Environment & Credentials Config

> 25 nodes

## Key Concepts

- **Environment** (46 connections) — `wp1/environment.py`
- **credentials.py** (29 connections) — `wp1/credentials.py`
- **environment.py** (25 connections) — `wp1/environment.py`
- **oauth_test.py** (11 connections) — `wp1/web/oauth_test.py`
- **DevelopmentModeTest** (11 connections) — `wp1/web/oauth_test.py`
- **config.py** (10 connections) — `wp1/config.py`
- **wp1/db.py** (8 connections) — `wp1/db.py`
- **cron_config.py** (7 connections) — `cron_config.py`
- **wiki_db.py** (7 connections) — `wp1/wiki_db.py`
- **app_logging_test.py** (5 connections) — `wp1/app_logging_test.py`
- **AppLoggingTest** (4 connections) — `wp1/app_logging_test.py`
- **wiki_db_test.py** (4 connections) — `wp1/wiki_db_test.py`
- **wp10_db_test.py** (4 connections) — `wp1/wp10_db_test.py`
- **.test_configure_logging()** (3 connections) — `wp1/app_logging_test.py`
- **Config** (3 connections) — `wp1/config.py`
- **WikiDbTest** (3 connections) — `wp1/wiki_db_test.py`
- **Wp10DbTest** (3 connections) — `wp1/wp10_db_test.py`
- **Recurring job definitions for RQ's built-in cron scheduler. Run by the…** (1 connections) — `cron_config.py`
- **patch** (1 connections)
- **This is a pytest test class, because we want to use the `caplog` fixture.** (1 connections) — `wp1/app_logging_test.py`
- **Central configuration module for WP1. Reads configuration from environment…** (1 connections) — `wp1/config.py`
- **Backwards-compatible adapter for the credentials system. This file reads from…** (1 connections) — `wp1/credentials.py`
- **tests for the development mode OAuth bypass functionality.** (1 connections) — `wp1/web/oauth_test.py`
- **.test_connect_works()** (1 connections) — `wp1/wiki_db_test.py`
- **.test_connect_works()** (1 connections) — `wp1/wp10_db_test.py`

## Relationships

- [DB Test Harness](DB_Test_Harness.md) (10 shared connections)
- [OAuth Web Tests](OAuth_Web_Tests.md) (10 shared connections)
- [Config Parsing Tests](Config_Parsing_Tests.md) (9 shared connections)
- [Storage Test](Storage_Test.md) (7 shared connections)
- [Builder & Selection Logic](Builder_%26_Selection_Logic.md) (6 shared connections)
- [DB Connection Tests](DB_Connection_Tests.md) (6 shared connections)
- [Maintenance](Maintenance.md) (5 shared connections)
- [20220818 01 5X0T9 Add Object](20220818_01_5X0T9_Add_Object.md) (5 shared connections)
- [Flask App Tests](Flask_App_Tests.md) (5 shared connections)
- [Job Queues](Job_Queues.md) (4 shared connections)
- [ZIM Email Endpoints](ZIM_Email_Endpoints.md) (4 shared connections)
- [Dev Project Stubs](Dev_Project_Stubs.md) (4 shared connections)

## Source Files

- `cron_config.py`
- `wp1/app_logging_test.py`
- `wp1/config.py`
- `wp1/credentials.py`
- `wp1/db.py`
- `wp1/environment.py`
- `wp1/web/oauth_test.py`
- `wp1/wiki_db.py`
- `wp1/wiki_db_test.py`
- `wp1/wp10_db_test.py`

## Audit Trail

- EXTRACTED: 162 (85%)
- INFERRED: 29 (15%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
