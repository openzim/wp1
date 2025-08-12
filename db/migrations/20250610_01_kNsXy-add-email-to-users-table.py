"""
Add email column to users table
"""

from yoyo import step

__depends__ = {'20250426_01_i656U-drop-logging-table'}

steps = [
    step(
        "ALTER TABLE users ADD COLUMN u_email VARBINARY(255) NULL",
        "ALTER TABLE users DROP COLUMN u_email"
    )
]
