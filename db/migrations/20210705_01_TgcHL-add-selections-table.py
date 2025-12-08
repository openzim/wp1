"""
Add selections table
"""

from yoyo import step

__depends__ = {"20210528_01_xt830-add-users-table"}

steps = [
    step(
        "CREATE TABLE selections ("
        "s_id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT, "
        "s_name VARBINARY(255) NOT NULL, "
        "s_user_id INTEGER NOT NULL, "
        "s_hash VARBINARY(255), "
        "s_project VARBINARY(255) NOT NULL, "
        "s_model VARBINARY(255), "
        "s_region VARBINARY(255), "
        "s_bucket VARBINARY(255), "
        "s_object_key VARBINARY(255), "
        "s_last_generated BINARY(20)"
        ")",
        "DROP TABLE selections",
    )
]
