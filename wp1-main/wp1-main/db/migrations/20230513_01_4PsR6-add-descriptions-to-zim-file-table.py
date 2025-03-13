"""
Add descriptions to zim file table
"""

from yoyo import step

__depends__ = {'20230429_01_e8yCB-add-zim-file-versions'}

steps = [
    step("ALTER TABLE zim_files ADD COLUMN z_long_description BLOB",
         "ALTER TABLE zim_files DROP COLUMN z_long_description"),
    step("ALTER TABLE zim_files ADD COLUMN z_description TINYBLOB",
         "ALTER TABLE zim_files DROP COLUMN z_description")
]
