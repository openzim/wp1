"""
List builders table
"""

from yoyo import step

__depends__ = {"20210724_01_p2yUM-remove-deprecated-selections-table"}

steps = [
    step(
        "CREATE TABLE builders ("
        "s_id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT, "
        "s_name VARBINARY(255) NOT NULL, "
        "s_user_id INTEGER NOT NULL, "
        "s_project VARBINARY(255) NOT NULL, "
        "s_params BLOB, "
        "s_created_at BINARY(20), "
        "s_updated_at BINARY(20)"
        ")",
        "DROP TABLE builders",
    )
]
