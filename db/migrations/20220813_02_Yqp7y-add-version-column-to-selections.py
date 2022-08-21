"""
Add version column to selections
"""

from yoyo import step

__depends__ = {'20220813_01_rhr0D-add-current-version-column-to-builders'}

steps = [
    step("ALTER TABLE selections ADD COLUMN (s_version INTEGER NOT NULL)",
         "ALTER TABLE selections DROP COLUMN s_version"),
    step("UPDATE selections SET s_version = 1")
]
