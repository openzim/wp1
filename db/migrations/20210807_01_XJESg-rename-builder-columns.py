"""
RENAME builders columns
"""

from yoyo import step

__depends__ = {"20210728_01_eJYGE-add-model-to-builders"}

steps = [
    step(
        "ALTER TABLE builders "
        "CHANGE COLUMN s_id b_id INTEGER AUTO_INCREMENT, "
        "CHANGE COLUMN s_name b_name VARBINARY(255), "
        "CHANGE COLUMN s_user_id b_user_id INTEGER, "
        "CHANGE COLUMN s_project b_project VARBINARY(255), "
        "CHANGE COLUMN s_params b_params BLOB, "
        "CHANGE COLUMN s_created_at b_created_at BINARY(20), "
        "CHANGE COLUMN s_updated_at b_updated_at BINARY(20)",
        "ALTER TABLE builders "
        "CHANGE COLUMN b_id s_id INTEGER AUTO_INCREMENT, "
        "CHANGE COLUMN b_name s_name VARBINARY(255), "
        "CHANGE COLUMN b_user_id s_user_id INTEGER, "
        "CHANGE COLUMN b_project s_project VARBINARY(255), "
        "CHANGE COLUMN b_params s_params BLOB, "
        "CHANGE COLUMN b_created_at s_created_at BINARY(20), "
        "CHANGE COLUMN b_updated_at s_updated_at BINARY(20)",
    )
]
