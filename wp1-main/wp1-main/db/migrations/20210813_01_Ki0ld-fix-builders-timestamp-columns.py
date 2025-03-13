"""
Fix builders timestamp columns
"""

from yoyo import step

__depends__ = {'20210807_01_XJESg-rename-builder-columns'}

steps = [
    step(
        "ALTER TABLE builders "
        "CHANGE COLUMN b_created_at b_created_at BINARY(14), "
        "CHANGE COLUMN b_updated_at b_updated_at BINARY(14)",
        "ALTER TABLE builders "
        "CHANGE COLUMN b_created_at b_created_at BINARY(20), "
        "CHANGE COLUMN b_updated_at b_updated_at BINARY(20)")
]
