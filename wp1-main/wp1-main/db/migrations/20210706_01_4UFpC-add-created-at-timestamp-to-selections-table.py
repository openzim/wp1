"""
Add created_at timestamp to selections table
"""

from yoyo import step

__depends__ = {'20210705_01_TgcHL-add-selections-table'}

steps = [
    step("ALTER TABLE selections ADD COLUMN (s_created_at BINARY(20))",
         "ALTER TABLE selections DROP COLUMN s_created_at")
]
