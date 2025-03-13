"""
Remove DEFAULT for s_zimfarm_status
"""

from yoyo import step

__depends__ = {'20230326_01_hOgak-add-zim-file-updated-at-to-selections'}

steps = [
    step(
        'ALTER TABLE selections CHANGE COLUMN s_zimfarm_status s_zimfarm_status VARBINARY(255) DEFAULT "NOT_REQUESTED"',
        'ALTER TABLE selections CHANGE COLUMN s_zimfarm_status s_zimfarm_status VARBINARY(255) DEFAULT "REQUESTED"',
    )
]
