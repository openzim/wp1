"""
Create zimfarm fields on selections
"""

from yoyo import step

__depends__ = {'20221113_03_xzm65-allow-selections-null-object-key'}

steps = [
    step(
        'ALTER TABLE selections ADD COLUMN ('
        '  s_zimfarm_task_id VARBINARY(255),'
        '  s_zimfarm_error_messages BLOB, '
        '  s_zimfarm_status VARBINARY(255) DEFAULT "REQUESTED")',
        'ALTER TABLE selections DROP s_zimfarm_task_id, DROP s_zimfarm_error_messages, DROP s_zimfarm_status'
    )
]
