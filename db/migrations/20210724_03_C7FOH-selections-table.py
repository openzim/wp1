"""
Selections table
"""

from yoyo import step

__depends__ = {'20210724_02_PR3Js-list-builders-table'}

steps = [
    step(
        "CREATE TABLE selections ("
        "s_id VARBINARY(255) NOT NULL PRIMARY KEY, "
        "s_builder_id INTEGER NOT NULL, "
        "s_content_type VARBINARY(255) NOT NULL, "
        "s_updated_at BINARY(20) NOT NULL"
        ")", "DROP TABLE selections")
]
