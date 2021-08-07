"""
RENAME builders columns
"""

from yoyo import step

__depends__ = {'20210728_01_eJYGE-add-model-to-builders'}

steps = [
    step("ALTER TABLE builders"
         "RENAME COLUMN s_id TO b_id, "
         "RENAME COLUMN s_name TO b_name, "
         "RENAME COLUMN s_user_id TO b_user_id, "
         "RENAME COLUMN s_project TO b_project, "
         "RENAME COLUMN s_params TO b_params, "
         "RENAME COLUMN s_created_at TO b_created_at, "
         "RENAME COLUMN s_updated_at TO b_updated_at")
]
