"""
This migration adds 'interval_between_zim_generations' and 'remaining_generations' to the zim_schedules table.
"""

from yoyo import step

__depends__ = {'20250610_02_FHB8A-create-zim-schedules-table'}

steps = [
    step(
        'ALTER TABLE zim_schedules ADD COLUMN s_interval_between_zim_generations INTEGER NULL, ADD COLUMN s_remaining_generations INTEGER NULL',
        'ALTER TABLE zim_schedules DROP COLUMN s_interval_between_zim_generations, DROP COLUMN s_remaining_generations'
    )
]
