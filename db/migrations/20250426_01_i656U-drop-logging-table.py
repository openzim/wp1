"""
Drop logging table
"""

from yoyo import step

__depends__ = {
    '20250325_01_sFddz-add-article-count-to-selection-table',
    '20250330_01_zaRQa-migrate-last-7-days-of-logs'
}

steps = [step('DROP TABLE IF EXISTS logging')]
