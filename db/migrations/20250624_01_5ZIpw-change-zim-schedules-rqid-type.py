"""

"""

from yoyo import step

__depends__ = {'20250621_01_A5B6C-add-interval-and-remaining-gens-to-zim-schedules'}

steps = [
    step(
        "ALTER TABLE zim_schedules "
        "MODIFY COLUMN s_rq_job_id VARCHAR(36)",
        "ALTER TABLE zim_schedules "
        "MODIFY COLUMN s_rq_job_id INTEGER"
    )
]
