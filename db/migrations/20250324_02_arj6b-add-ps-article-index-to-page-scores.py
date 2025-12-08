"""
Add index to ps_article in page_scores
"""

from yoyo import step

__depends__ = {"20240429_01_qtSms-add-scores-table"}

steps = [
    step(
        "ALTER TABLE page_scores ADD KEY `idx_ps_article` (ps_article);",
        "ALTER TABLE page_scores DROP INDEX `idx_ps_article`;",
    )
]
