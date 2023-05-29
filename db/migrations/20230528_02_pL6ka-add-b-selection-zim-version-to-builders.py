"""
Add b_selection_zim_version to builders
"""

from yoyo import step

__depends__ = {'20230528_01_cSwUS-remove-selection-and-zim-file-versions'}

steps = [
    step(
        'ALTER TABLE builders ADD COLUMN b_selection_zim_version INTEGER NOT NULL DEFAULT 0',
        'ALTER TABLE builders DROP COLUMN b_selection_zim_version',
    ),
    step('UPDATE builders SET b_selection_zim_version = b_current_version')
]
