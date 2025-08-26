"""
Add email confirmation token column to zim_schedules table
"""

from yoyo import step

__depends__ = {'20250729_01_8hH6B-refactor-zim-schedules-zim-files'}

steps = [
    step(
        'ALTER TABLE zim_schedules '
        '  ADD COLUMN s_email_confirmation_token VARBINARY(255) NULL',
        'ALTER TABLE zim_schedules '
        '  DROP COLUMN s_email_confirmation_token'
    )
]
