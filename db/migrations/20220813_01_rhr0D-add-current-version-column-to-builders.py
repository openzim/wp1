"""
Add current_version column to builders
"""

from yoyo import step

__depends__ = {'20210724_03_C7FOH-selections-table'}

steps = [
    step(
        "ALTER TABLE builders ADD COLUMN (b_current_version VARBINARY(255) NOT NULL)",
        "ALTER TABLE builders DROP COLUMN b_current_version")
]
