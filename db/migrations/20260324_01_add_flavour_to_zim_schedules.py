"""
Add flavour column to zim_schedules table for ZIM format selection
"""

from yoyo import step

__depends__ = {"20250821_01_add_email_confirmation_token_to_zim_schedules"}

steps = [
    step(
        "ALTER TABLE zim_schedules " "  ADD COLUMN s_flavour VARBINARY(50) NULL",
        "ALTER TABLE zim_schedules " "  DROP COLUMN s_flavour",
    )
]
