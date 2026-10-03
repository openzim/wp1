# Page Move Logic Tests

> 30 nodes

## Key Concepts

- **BaseCombinedDbTest** (31 connections) — `wp1/base_db_test.py`
- **logic/page_test.py** (25 connections) — `wp1/logic/page_test.py`
- **LogicPageMovesTest** (19 connections) — `wp1/logic/page_test.py`
- **LogicPageMoveDbTest** (15 connections) — `wp1/logic/page_test.py`
- **LogicPageCategoryTest** (13 connections) — `wp1/logic/page_test.py`
- **Namespace** (7 connections) — `wp1/models/wp10/namespace.py`
- **TestCleanupDb** (6 connections) — `wp1/base_db_test.py`
- **patch** (6 connections)
- **NsType** (5 connections) — `wp1/models/wp10/namespace.py`
- **.setUp()** (4 connections) — `wp1/logic/page_test.py`
- **namespace.py** (4 connections) — `wp1/models/wp10/namespace.py`
- **get_all_moves()** (3 connections) — `wp1/logic/page_test.py`
- **get_all_logs()** (3 connections) — `wp1/logic/page_test.py`
- **.setUp()** (2 connections) — `wp1/logic/page_test.py`
- **.setUp()** (2 connections) — `wp1/logic/page_test.py`
- **.test_no_redirect_no_move()** (2 connections) — `wp1/logic/page_test.py`
- **.test_get_redirect_from_api()** (2 connections) — `wp1/logic/page_test.py`
- **.test_get_single_move_from_api()** (2 connections) — `wp1/logic/page_test.py`
- **.test_get_most_recent_move_from_api()** (2 connections) — `wp1/logic/page_test.py`
- **.test_get_redirect_too_old_from_api()** (2 connections) — `wp1/logic/page_test.py`
- **.test_get_single_move_too_old_from_api()** (2 connections) — `wp1/logic/page_test.py`
- **.test_does_not_add_existing_move()** (2 connections) — `wp1/logic/page_test.py`
- **.test_does_not_add_existing_log()** (2 connections) — `wp1/logic/page_test.py`
- **.test_no_op()** (1 connections) — `wp1/base_db_test.py`
- **.test_get_category_pages()** (1 connections) — `wp1/logic/page_test.py`
- _... and 5 more nodes in this community_

## Relationships

- [Project & Page Models](Project_%26_Page_Models.md) (15 shared connections)
- [DB Test Harness](DB_Test_Harness.md) (14 shared connections)
- [Log Model](Log_Model.md) (8 shared connections)
- [Page Logic](Page_Logic.md) (8 shared connections)
- [Constants & Utilities](Constants_%26_Utilities.md) (7 shared connections)
- [Assessment Tables & Categories](Assessment_Tables_%26_Categories.md) (5 shared connections)
- [Rating Model Tests](Rating_Model_Tests.md) (3 shared connections)
- [Environment & Credentials Config](Environment_%26_Credentials_Config.md) (2 shared connections)
- [Selection & Meta Builder](Selection_%26_Meta_Builder.md) (2 shared connections)
- [Flask App Tests](Flask_App_Tests.md) (2 shared connections)
- [Project Test](Project_Test.md) (1 shared connections)
- [Project Assessment Tests](Project_Assessment_Tests.md) (1 shared connections)

## Source Files

- `wp1/base_db_test.py`
- `wp1/logic/page_test.py`
- `wp1/models/wp10/namespace.py`

## Audit Trail

- EXTRACTED: 110 (65%)
- INFERRED: 58 (35%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
