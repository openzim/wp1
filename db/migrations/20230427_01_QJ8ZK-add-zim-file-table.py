"""
Add ZIM file table
"""

from yoyo import step

__depends__ = {'20230423_01_9nFkK-add-s-zim-file-requested-at'}

steps = [
    step(
        'CREATE TABLE zim_files ('
        '  z_id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,'
        '  z_selection_id VARBINARY(255) NOT NULL,'
        '  z_status VARBINARY(255) DEFAULT "NOT_REQUESTED",'
        '  z_task_id VARBINARY(255),'
        '  z_requested_at BINARY(14),'
        '  z_updated_at BINARY(14)'
        ')', 'DROP TABLE zim_files'),
    step(
        'INSERT INTO zim_files (z_selection_id, z_task_id, z_status, z_requested_at, z_updated_at) '
        'SELECT s_id, s_zimfarm_task_id, s_zimfarm_status, s_zim_file_requested_at, s_zim_file_updated_at '
        'FROM selections WHERE s_zimfarm_task_id IS NOT NULL',
        'DELETE FROM zim_files')
]
