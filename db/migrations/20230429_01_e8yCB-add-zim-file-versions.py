"""
Add zim file versions
"""

from yoyo import step

__depends__ = {'20230427_02_Sareg-drop-selections-zim-file-fields'}

steps = [
    step('ALTER TABLE zim_files ADD COLUMN z_version INTEGER',
         'ALTER TABLE zim_files DROP COLUMN z_version'),
    step('ALTER TABLE selections ADD COLUMN s_zim_version INTEGER',
         'ALTER TABLE selections DROP COLUMN s_zim_version'),
    step('UPDATE selections SET s_zim_version = 1'),
    step('UPDATE zim_files SET z_version = 1'),
]
