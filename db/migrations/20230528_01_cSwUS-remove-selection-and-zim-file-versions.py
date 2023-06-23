"""
Remove selection and zim_file versions
"""

from yoyo import step

__depends__ = {'20230513_01_4PsR6-add-descriptions-to-zim-file-table'}

steps = [
    step('ALTER TABLE selections DROP COLUMN s_zim_version',
         'ALTER TABLE selections ADD COLUMN s_zim_version INTEGER'),
    step('ALTER TABLE zim_files DROP COLUMN z_version',
         'ALTER TABLE selections ADD COLUMN z_version INTEGER'),
]
