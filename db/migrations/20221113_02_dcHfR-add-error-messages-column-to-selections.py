"""
Add error_messages column to selections
"""

from yoyo import step

__depends__ = {'20221113_01_GslXq-add-status-columns-to-selections'}

steps = [
    step("ALTER TABLE selections ADD COLUMN s_error_messages BLOB",
         "ALTER TABLE selections DROP COLUMN s_error_messages")
]
