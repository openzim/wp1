"""
Add metric columns to temp_pageviews and page_scores
"""

from yoyo import step

__depends__ = {"20260824_01_6cHdk-delete-book-builders-and-their-selections"}

steps = [
    step(
        "ALTER TABLE temp_pageviews"
        "  ADD COLUMN tp_size INTEGER DEFAULT 0,"
        "  ADD COLUMN tp_links INTEGER DEFAULT 0,"
        "  ADD COLUMN tp_lang_links INTEGER DEFAULT 0,"
        "  ADD COLUMN tp_score INTEGER DEFAULT 0",
        "ALTER TABLE temp_pageviews"
        "  DROP COLUMN tp_size,"
        "  DROP COLUMN tp_links,"
        "  DROP COLUMN tp_lang_links,"
        "  DROP COLUMN tp_score",
    ),
    step(
        "ALTER TABLE page_scores  ADD COLUMN ps_size INTEGER DEFAULT 0",
        "ALTER TABLE page_scores  DROP COLUMN ps_size",
    ),
    step(
        "CREATE INDEX idx_page_scores_lang_score ON page_scores(ps_lang, ps_score DESC)",
        "DROP INDEX idx_page_scores_lang_score ON page_scores",
    ),
    step(
        "CREATE INDEX idx_ratings_article ON ratings(r_article)",
        "DROP INDEX idx_ratings_article ON ratings",
    ),
]
