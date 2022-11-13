"""
Add status columns to selections
"""

from yoyo import step

__depends__ = {'20221023_01_lwlVT-create-custom-table'}

steps = [
    step(
        'ALTER TABLE selections ADD COLUMN s_status VARBINARY(255) DEFAULT "OK"',
        'ALTER TABLE selections DROP COLUMN s_status'),
]
