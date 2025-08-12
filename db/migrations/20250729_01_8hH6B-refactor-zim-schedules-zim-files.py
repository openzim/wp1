"""
Migration to update zim_files and zim_schedules tables:
- Rename zim_files table to zim_tasks
- Alter zim_schedules: remove s_zim_file_id, make s_rq_job_id nullable, add s_long_description, s_description, s_title
"""

from yoyo import step

__depends__ = set()

steps = [
  # Step 1: Add z_zim_schedule_id column to zim_files
  step(
    '''
    ALTER TABLE zim_files 
    ADD COLUMN z_zim_schedule_id VARBINARY(36) NULL
    ''',
    '''
    ALTER TABLE zim_files 
    DROP COLUMN z_zim_schedule_id
    '''
  ),
  
  # Step 2: Add title/description columns to zim_schedules and make s_rq_job_id nullable
  step(
    '''
    ALTER TABLE zim_schedules
    ADD COLUMN s_title blob,
    ADD COLUMN s_description blob,
    ADD COLUMN s_long_description mediumblob,
    MODIFY COLUMN s_rq_job_id VARBINARY(36) NULL
    ''',
    '''
    ALTER TABLE zim_schedules
    DROP COLUMN s_title,
    DROP COLUMN s_description,
    DROP COLUMN s_long_description,
    MODIFY COLUMN s_rq_job_id VARBINARY(36) NOT NULL
    '''
  ),
  
  # Step 3: Insert new zim_schedules rows based on zim_files data (in the rollback we want to keep the existing zim_schedules data)
  step(
    '''
    INSERT INTO zim_schedules (
        s_id,
        s_builder_id,
        s_rq_job_id,
        s_interval,
        s_remaining_generations,
        s_email,
        s_last_updated_at,
        s_long_description,
        s_description,
        s_title,
        s_zim_file_id
    )
    SELECT
        UUID(),
        s.s_builder_id,
        NULL,
        NULL,
        NULL,
        NULL,
        NOW(),
        zf.z_long_description,
        zf.z_description,
        zf.z_title,
        zf.z_id
    FROM zim_files zf
    JOIN selections s ON zf.z_selection_id = s.s_id
    ''',
    '''
    DELETE FROM zim_schedules
    '''
  ),
  
  # Step 4: Update z_zim_schedule_id in zim_files to link to new schedules
  step(
    '''
    UPDATE zim_files zf
    JOIN zim_schedules zs ON zs.s_zim_file_id = zf.z_id
    SET zf.z_zim_schedule_id = zs.s_id
    ''',
    '''
    UPDATE zim_files 
    SET z_zim_schedule_id = NULL
    '''
  ),
  
  # Step 5: Drop s_zim_file_id column from zim_schedules
  step(
    '''
    ALTER TABLE zim_schedules
    DROP COLUMN s_zim_file_id
    ''',
    '''
    UPDATE zim_schedules zs
    JOIN zim_files zf ON zs.s_id = zf.z_zim_schedule_id
    SET zs.s_zim_file_id = zf.z_id
    '''
  ),
  step(
    '''
    -- no forward migration needed
    ''',
    '''
    ALTER TABLE zim_schedules
    ADD COLUMN s_zim_file_id INTEGER NULL;
    '''
  ),

  # Step 6: Drop title/description columns from zim_files
  step(
    '''
    ALTER TABLE zim_files
    DROP COLUMN z_title,
    DROP COLUMN z_description,
    DROP COLUMN z_long_description
    ''',
    '''
    UPDATE zim_files zf
    JOIN zim_schedules zs ON zf.z_zim_schedule_id = zs.s_id
    SET zf.z_title = zs.s_title,
        zf.z_description = zs.s_description,
        zf.z_long_description = zs.s_long_description
    '''
  ),
  step(
    '''
    -- no forward migration needed
    ''',
    '''
    ALTER TABLE zim_files
    ADD COLUMN z_title tinyblob,
    ADD COLUMN z_description tinyblob,
    ADD COLUMN z_long_description blob;
    '''
  ),
  
  # Step 7: Rename zim_files to zim_tasks
  step(
    '''
    ALTER TABLE zim_files RENAME TO zim_tasks
    ''',
    '''
    ALTER TABLE zim_tasks RENAME TO zim_files
    '''
  ),
]
   