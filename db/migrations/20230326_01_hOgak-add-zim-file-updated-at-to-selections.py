"""
Add zim_file_updated_at to selections
"""

from yoyo import step

__depends__ = {'20230316_01_eMzhU-create-zimfarm-fields-on-selections'}

steps = [
    step('ALTER TABLE selections ADD COLUMN s_zim_file_updated_at BINARY(14)',
         'ALTER TABLE selections DROP s_zim_file_updated_at')
]
