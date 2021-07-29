"""
Remove deprecated selections table
"""

from yoyo import step

__depends__ = {'20210706_01_4UFpC-add-created-at-timestamp-to-selections-table'}

steps = [step("DROP TABLE selections")]
