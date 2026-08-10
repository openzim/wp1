# Pageview Scores

> 40 nodes

## Key Concepts

- **ScoresTest** (26 connections) — `wp1/scores_test.py`
- **scores.py** (23 connections) — `wp1/scores.py`
- **patch** (17 connections)
- **update_pageviews()** (8 connections) — `wp1/scores.py`
- **Wp1ScoreProcessingError** (7 connections) — `wp1/exceptions.py`
- **download_pageviews()** (6 connections) — `wp1/scores.py`
- **get_pageview_url()** (5 connections) — `wp1/scores.py`
- **get_prev_file_path()** (4 connections) — `wp1/scores.py`
- **get_cur_file_path()** (4 connections) — `wp1/scores.py`
- **get_pageview_file_path()** (3 connections) — `wp1/scores.py`
- **pageview_components()** (3 connections) — `wp1/scores.py`
- **wiki_languages()** (2 connections) — `wp1/scores.py`
- **raw_pageviews()** (2 connections) — `wp1/scores.py`
- **reset_missing_articles_pageviews()** (2 connections) — `wp1/scores.py`
- **insert_temp_pageviews()** (2 connections) — `wp1/scores.py`
- **swap_temp_pageviews_to_scores()** (2 connections) — `wp1/scores.py`
- **truncate_temp_pageviews()** (2 connections) — `wp1/scores.py`
- **.test_wiki_languages()** (2 connections) — `wp1/scores_test.py`
- **.test_wiki_languages_raises_on_http_error()** (2 connections) — `wp1/scores_test.py`
- **.test_get_pageview_url()** (2 connections) — `wp1/scores_test.py`
- **.test_get_pageview_url_prev()** (2 connections) — `wp1/scores_test.py`
- **.test_get_prev_file_path()** (2 connections) — `wp1/scores_test.py`
- **.test_get_cur_file_path()** (2 connections) — `wp1/scores_test.py`
- **.test_download_pageviews()** (2 connections) — `wp1/scores_test.py`
- **.test_download_pageviews_remove_prev()** (2 connections) — `wp1/scores_test.py`
- _... and 15 more nodes in this community_

## Relationships

- [DB Test Harness](DB_Test_Harness.md) (4 shared connections)
- [Selection Builder Framework](Selection_Builder_Framework.md) (2 shared connections)
- [Constants & Utilities](Constants_%26_Utilities.md) (2 shared connections)
- [Log Upload](Log_Upload.md) (2 shared connections)
- [MediaWiki API Client](MediaWiki_API_Client.md) (2 shared connections)
- [Builder & Selection Logic](Builder_%26_Selection_Logic.md) (1 shared connections)
- [20220818 01 5X0T9 Add Object](20220818_01_5X0T9_Add_Object.md) (1 shared connections)
- [Environment & Credentials Config](Environment_%26_Credentials_Config.md) (1 shared connections)
- [Init Test](Init_Test.md) (1 shared connections)

## Source Files

- `wp1/exceptions.py`
- `wp1/scores.py`
- `wp1/scores_test.py`

## Audit Trail

- EXTRACTED: 155 (98%)
- INFERRED: 3 (2%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
