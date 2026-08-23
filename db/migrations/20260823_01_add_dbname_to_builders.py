"""
Add dbname column to builders table, cached from the sitematrix
"""

from yoyo import step

__depends__ = {"20260324_01_add_flavour_to_zim_schedules"}

steps = [
    step(
        "ALTER TABLE builders " "  ADD COLUMN b_dbname VARBINARY(255) NULL",
        "ALTER TABLE builders " "  DROP COLUMN b_dbname",
    )
]
