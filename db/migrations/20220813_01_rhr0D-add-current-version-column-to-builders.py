"""
Add current_version column to builders
"""

from yoyo import step

__depends__ = {"20210813_02_g8XdS-fix-selections-timestamp-columns"}

steps = [
    step(
        "ALTER TABLE builders ADD COLUMN (b_current_version INTEGER NOT NULL DEFAULT 0)",
        "ALTER TABLE builders DROP COLUMN b_current_version",
    ),
    step("UPDATE builders SET b_current_version = 1"),
]
