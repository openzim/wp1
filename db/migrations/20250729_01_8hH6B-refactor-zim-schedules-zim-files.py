"""
Migration to update zim_files and zim_schedules tables:
- Rename zim_files table to zim_tasks
- Alter zim_schedules: remove s_zim_file_id, make s_rq_job_id nullable, add s_long_description, s_description, s_title
"""

from yoyo import step

__depends__ = set()

steps = [
  step(
    '''
    ALTER TABLE zim_files
      RENAME zim_tasks, 
      DROP COLUMN z_title, 
      DROP COLUMN z_description, 
      DROP COLUMN z_long_description, 
      ADD COLUMN z_zim_schedule_id VARBINARY(36) NULL
    ''',
    '''
    ALTER TABLE zim_tasks 
      RENAME zim_files, 
      DROP COLUMN z_zim_schedule_id, 
      ADD COLUMN z_title tinyblob, 
      ADD COLUMN z_description tinyblob, 
      ADD COLUMN z_long_description blob
    '''
  ),
  step(
      '''
    ALTER TABLE zim_schedules
      DROP COLUMN s_zim_file_id,
      MODIFY COLUMN s_rq_job_id VARBINARY(36) NULL,
      ADD COLUMN s_long_description blob,
      ADD COLUMN s_description tinyblob,
      ADD COLUMN s_title tinyblob
    ''',
    '''
    ALTER TABLE zim_schedules
      DROP COLUMN s_long_description,
      DROP COLUMN s_description,
      DROP COLUMN s_title,
      ADD COLUMN s_zim_file_id INTEGER NULL,
      MODIFY COLUMN s_rq_job_id VARBINARY(36) NOT NULL
    '''
  ),
]
