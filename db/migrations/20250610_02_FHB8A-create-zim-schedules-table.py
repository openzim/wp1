"""
This migration creates the zim_schedules table.
"""

from yoyo import step

__depends__ = {"20250610_01_kNsXy-add-email-to-users-table"}

steps = [
    step(
        "CREATE TABLE zim_schedules ("
        "  s_id VARBINARY(36) NOT NULL PRIMARY KEY,"
        "  s_builder_id VARBINARY(255) NOT NULL,"  # ID in the builders table
        "  s_zim_file_id INTEGER NULL,"  # Last ZIM file related to the schedule, can be NULL
        "  s_rq_job_id VARBINARY(36) NOT NULL,"  # ID of the job in the rq-scheduler
        "  s_interval INTEGER NULL,"  # Interval between ZIM generations
        "  s_remaining_generations INTEGER NULL,"  # Remaining generations to be created
        "  s_email VARBINARY(255) NULL,"  # Email to notify when the zim generation is done
        "  s_last_updated_at BINARY(14) NOT NULL"  # Last update to the schedule
        ")",
        "DROP TABLE zim_schedules",
    )
]
