"""
Allow selections NULL object key
"""

from yoyo import step

__depends__ = {'20221113_02_dcHfR-add-error-messages-column-to-selections'}

steps = [
    step(
        "ALTER TABLE selections MODIFY COLUMN s_object_key VARBINARY(255)",
        "ALTER TABLE selections MODIFY COLUMN s_object_key VARBINARY(255) NOT NULL"
    )
]
