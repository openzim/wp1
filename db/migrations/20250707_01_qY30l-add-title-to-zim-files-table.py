"""

"""

from yoyo import step

__depends__ = {'20250610_02_FHB8A-create-zim-schedules-table'}

steps = [
    step( 'ALTER TABLE zim_files '
          '  ADD COLUMN z_title TINYBLOB NULL',
          'ALTER TABLE zim_files '
          '  DROP COLUMN z_title'
        )
]
