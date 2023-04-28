"""
Drop selections zim file fields
"""

from yoyo import step

__depends__ = {'20230427_01_QJ8ZK-add-zim-file-table'}

steps = [
    step(
        'ALTER TABLE selections'
        '  DROP s_zimfarm_status, DROP s_zimfarm_error_messages, DROP s_zimfarm_task_id,'
        '  DROP s_zim_file_requested_at, DROP s_zim_file_updated_at'),
]
