"""
Add temp_pageviews table
"""

from yoyo import step

__depends__ = {'20240429_01_qtSms-add-scores-table'}

steps = [
    step(
        '''
        CREATE TABLE temp_pageviews (
            tp_lang VARBINARY(255),
            tp_page_id INTEGER NOT NULL,
            tp_article VARBINARY(1024),
            tp_views INTEGER DEFAULT 0,
            PRIMARY KEY (`tp_lang`, `tp_page_id`),
            KEY `idx_tp_article` (tp_article)
        )
        ''',
        'DROP TABLE temp_pageviews',
    )
]
