"""
Create database tables for custom article tables.
"""

from yoyo import step

__depends__ = {'20220905_01_4yJzk-change-builder-id-column'}

steps = [
    step(
        "CREATE TABLE custom ("
        "c_name VARBINARY(255) NOT NULL PRIMARY KEY, "
        "c_module VARBINARY(255) NOT NULL, "
        "c_username VARBINARY(255) DEFAULT NULL, "
        "c_description BLOB,"
        "c_params MEDIUMBLOB, "
        "c_created_at BINARY(20), "
        "c_updated_at BINARY(20), "
        "c_is_active TINYINT "
        ")", "DROP TABLE custom"),
    step(
        '''
      INSERT INTO custom (c_name, c_module, c_username, c_description, c_params, c_created_at, c_updated_at, c_is_active) VALUES
        ('us_roads', 'wp1.custom_tables.us_roads', 'Audiodude', 'First attempt at custom table for US roads project',
         '{"wiki_path": "US-Roads-Test", "template": "us_roads.jinja2"}',
         '2022-10-23T00:00:00Z', '2022-10-23T00:00:00Z', 1
        )
    ''', 'DELETE FROM custom WHERE c_name = "us_roads"')
]
