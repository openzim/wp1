"""
Add users table
"""

from yoyo import step

__depends__ = {}

steps = [
    step(
        "CREATE TABLE users (u_id INTEGER PRIMARY KEY, u_username VARCHAR(255))",
        "DROP TABLE users",
    )
]
