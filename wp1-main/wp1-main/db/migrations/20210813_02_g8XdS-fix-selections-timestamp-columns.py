"""
Fix selections timestamp columns
"""

from yoyo import step

__depends__ = {'20210813_01_Ki0ld-fix-builders-timestamp-columns'}

steps = [
    step(
        "ALTER TABLE selections "
        "CHANGE COLUMN s_updated_at s_updated_at BINARY(14)",
        "ALTER TABLE selections "
        "CHANGE COLUMN s_updated_at s_updated_at BINARY(20)")
]
