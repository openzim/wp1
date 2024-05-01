"""
Add scores table
"""

from yoyo import step

__depends__ = {'20230528_02_pL6ka-add-b-selection-zim-version-to-builders'}

steps = [
    step(
        '''CREATE TABLE page_scores (
                ps_lang VARBINARY(255),
                ps_page_id INTEGER NOT NULL,
                ps_article VARBINARY(1024),
                ps_views INTEGER DEFAULT 0,
                ps_links INTEGER DEFAULT 0,
                ps_lang_links INTEGER DEFAULT 0,
                ps_score INTEGER DEFAULT 0,
                PRIMARY KEY (`ps_lang`, `ps_page_id`),
                KEY `lang_article` (`ps_lang`, `ps_article`)
            )''', 'DROP TABLE page_scores')
]
