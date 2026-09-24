"""
Add page_scores metrics and per-metric temp tables

Each metric is staged in its own temp table (mirroring temp_pageviews) so that
temp_pageviews only ever holds pageviews.
"""

from yoyo import step

__depends__ = {"20260824_01_6cHdk-delete-book-builders-and-their-selections"}

steps = [
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
    step(
        """
        CREATE TABLE temp_pagesize (
            tp_lang VARBINARY(255),
            tp_page_id INTEGER NOT NULL,
            tp_article VARBINARY(1024),
            tp_size INTEGER DEFAULT 0,
            PRIMARY KEY (`tp_lang`, `tp_page_id`),
            KEY `idx_tp_article` (tp_article)
        )
        """,
        "DROP TABLE temp_pagesize",
    ),
    step(
        """
        CREATE TABLE temp_pagelinks (
            tp_lang VARBINARY(255),
            tp_page_id INTEGER NOT NULL,
            tp_article VARBINARY(1024),
            tp_links INTEGER DEFAULT 0,
            PRIMARY KEY (`tp_lang`, `tp_page_id`),
            KEY `idx_tp_article` (tp_article)
        )
        """,
        "DROP TABLE temp_pagelinks",
    ),
    step(
        """
        CREATE TABLE temp_pagelanglinks (
            tp_lang VARBINARY(255),
            tp_page_id INTEGER NOT NULL,
            tp_article VARBINARY(1024),
            tp_lang_links INTEGER DEFAULT 0,
            PRIMARY KEY (`tp_lang`, `tp_page_id`),
            KEY `idx_tp_article` (tp_article)
        )
        """,
        "DROP TABLE temp_pagelanglinks",
    ),
    step(
        """
        CREATE TABLE temp_pagescores (
            tp_lang VARBINARY(255),
            tp_page_id INTEGER NOT NULL,
            tp_article VARBINARY(1024),
            tp_score INTEGER DEFAULT 0,
            PRIMARY KEY (`tp_lang`, `tp_page_id`),
            KEY `idx_tp_article` (tp_article)
        )
        """,
        "DROP TABLE temp_pagescores",
    ),
    step(
        """
        CREATE TABLE temp_redirects (
            tr_lang VARBINARY(255),
            tr_source VARBINARY(1024),
            tr_target VARBINARY(1024),
            PRIMARY KEY (`tr_lang`, `tr_source`),
            KEY `idx_tr_target` (tr_lang, tr_target)
        )
        """,
        "DROP TABLE temp_redirects",
    ),
]
