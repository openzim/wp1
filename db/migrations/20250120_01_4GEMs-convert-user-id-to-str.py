"""
Convert user_id to VARCHAR
"""

from yoyo import step

__depends__ = {'20240429_01_qtSms-add-scores-table'}

steps = [
    step('ALTER TABLE users MODIFY u_id VARCHAR(255);',
         'ALTER TABLE users MODIFY u_id INT;'),
    step('ALTER TABLE builders MODIFY b_user_id VARCHAR(255);',
         'ALTER TABLE builders MODIFY b_user_id INT;'),
]
