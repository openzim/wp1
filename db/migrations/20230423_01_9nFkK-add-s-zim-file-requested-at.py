"""
Add s_zim_file_requested_at
"""

from yoyo import step

__depends__ = {'20230326_02_bTYKT-remove-default-for-s-zimfarm-status'}

steps = [
    step('ALTER TABLE selections ADD COLUMN s_zim_file_requested_at BINARY(14)',
         'ALTER TABLE selections DROP s_zim_file_requested_at')
]
