# Rating

> God node · 67 connections · `wp1/models/wp10/rating.py`

**Community:** [Rating Model Tests](Rating_Model_Tests.md)

## Connections by Relation

### calls

- \_get_all_ratings() `EXTRACTED`
- .\_insert_ratings() `EXTRACTED`
- update_project_assessments_by_kind() `EXTRACTED`
- process_unseen_articles() `EXTRACTED`
- .test_defers_log_for_new_article() `EXTRACTED`
- .setUp() `EXTRACTED`
- .setUp() `EXTRACTED`
- .test_logs_immediately_for_existing_changed_rating() `EXTRACTED`
- .test_no_deferred_log_for_existing_same_rating() `EXTRACTED`
- .test_returns_moved_article_refs() `EXTRACTED`
- .test_no_move_returns_empty_set() `EXTRACTED`
- get_project_rating_by_type() `EXTRACTED`
- get_random_article() `EXTRACTED`
- .test_empty_seen_returns_empty_moved() `EXTRACTED`
- get_project_ratings() `EXTRACTED`
- .\_insert_ratings() `EXTRACTED`
- .test_add_log_for_quality_rating() `EXTRACTED`
- .test_add_log_for_importance_rating() `EXTRACTED`
- .setUp() `EXTRACTED`

### contains

- wp10/rating.py `EXTRACTED`

### imports

- base_db_test.py `EXTRACTED`
- logic/project.py `EXTRACTED`
- logic/project_test.py `EXTRACTED`
- logic/rating.py `EXTRACTED`
- tables_test.py `EXTRACTED`
- logic/rating_test.py `EXTRACTED`
- wp10/rating_test.py `EXTRACTED`

### method

- .to_web_dict() `EXTRACTED`
- .\_get_namespace_prefix() `EXTRACTED`
- .\_make_article_link() `EXTRACTED`
- .\_make_article_history_link() `EXTRACTED`
- .\_make_article_talk_link() `EXTRACTED`
- .set_importance_timestamp_dt() `EXTRACTED`
- .set_quality_timestamp_dt() `EXTRACTED`
- .importance_timestamp_dt() `EXTRACTED`
- .quality_timestamp_dt() `EXTRACTED`

### references

- s `EXTRACTED`

### uses

- [BaseWpOneDbTest](BaseWpOneDbTest.md) `INFERRED`
- UpdateProjectAssessmentsTest `INFERRED`
- BaseCombinedDbTest `INFERRED`
- BaseWikiDbTest `INFERRED`
- TablesDbTest `INFERRED`
- GetProjectRatingByTypeTest `INFERRED`
- GetAllAssessmentNumbersTest `INFERRED`
- UpdateCategoryTest `INFERRED`
- ArticlesTest `INFERRED`
- UpdateProjectCategoriesByKindTest `INFERRED`
- DeferredLogMovedArticleTest `INFERRED`
- UpdateProjectRecordTest `INFERRED`
- UpdateProjectByNameTest `INFERRED`
- StoreNewRatingsTest `INFERRED`
- ProcessUnseenArticlesMovedTest `INFERRED`
- CleanupProjectTest `INFERRED`
- ProjectNamesTest `INFERRED`
- GlobalCountAndListTest `INFERRED`
- ProjectProgressTest `INFERRED`
- GlobalArticlesTest `INFERRED`

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
