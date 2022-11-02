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
        -- Start of JSON params, no unescaped ' allowed here
        '{
          "wiki_path": "US-Roads-Test",
          "template": "us_roads.jinja2",
          "parent_project": "U.S._road_transport",
          "aggregate_name": "State",
          "projects": [
            {
              "name": "Interstate_Highway_System",
              "alias": "IHS",
              "bgcolor": "silver"
            },
            {
              "name": "U.S._Highway_system",
              "alias": "USH",
              "bgcolor": "silver"
            },
            {
              "name": "U.S._auto_trail",
              "alias": "Auto trail",
              "bgcolor": "silver"
            },
            {
              "name": "Alabama_road_transport",
              "alias": "Alabama"
            },
            {
              "name": "Alaska_road_transport",
              "alias": "Alaska"
            },
            {
              "name": "American_Samoa_road_transport",
              "alias": "American Samoa",
              "bgcolor": "silver"
            },
            {
              "name": "Arizona_road_transport",
              "alias": "Arizona"
            },
            {
              "name": "Arkansas_road_transport",
              "alias": "Arkansas"
            },
            {
              "name": "California_road_transport",
              "alias": "California"
            },
            {
              "name": "Colorado_road_transport",
              "alias": "Colorado"
            },
            {
              "name": "Connecticut_road_transport",
              "alias": "Connecticut"
            },
            {
              "name": "Delaware_road_transport",
              "alias": "Delaware"
            },
            {
              "name": "District_of_Columbia_road_transport",
              "alias": "D.C.",
              "bgcolor": "silver"
            },
            {
              "name": "Florida_road_transport",
              "alias": "Florida"
            },
            {
              "name": "Georgia_(U.S._state)_road_transport",
              "alias": "Georgia"
            },
            {
              "name": "Guam_road_transport",
              "alias": "Guam",
              "bgcolor": "silver"
            },
            {
              "name": "Hawaii_road_transport",
              "alias": "Hawaii"
            },
            {
              "name": "Idaho_road_transport",
              "alias": "Idaho"
            },
            {
              "name": "Illinois_road_transport",
              "alias": "Illinois"
            },
            {
              "name": "Indiana_road_transport",
              "alias": "Indiana"
            },
            {
              "name": "Iowa_road_transport",
              "alias": "Iowa"
            },
            {
              "name": "Kansas_road_transport",
              "alias": "Kansas"
            },
            {
              "name": "Kentucky_road_transport",
              "alias": "Kentucky"
            },
            {
              "name": "Louisiana_road_transport",
              "alias": "Lousiana"
            },
            {
              "name": "Maine_road_transport",
              "alias": "Maine"
            },
            {
              "name": "Maryland_road_transport",
              "alias": "Maryland"
            },
            {
              "name": "Massachusetts_road_transport",
              "alias": "Massachusetts"
            },
            {
              "name": "Michigan_road_transport",
              "alias": "Michigan"
            },
            {
              "name": "Minnesota_road_transport",
              "alias": "Minnesota"
            },
            {
              "name": "Mississippi_road_transport",
              "alias": "Misssissippi"
            },
            {
              "name": "Missouri_road_transport",
              "alias": "Missouri"
            },
            {
              "name": "Montana_road_transport",
              "alias": "Montana"
            },
            {
              "name": "Nebraska_road_transport",
              "alias": "Nebraska"
            },
            {
              "name": "Nevada_road_transport",
              "alias": "Nevada"
            },
            {
              "name": "New_Hampshire_road_transport",
              "alias": "New Hampshire"
            },
            {
              "name": "New_Jersey_road_transport",
              "alias": "New Jersey"
            },
            {
              "name": "New_Mexico_road_transport",
              "alias": "New Mexico"
            },
            {
              "name": "New_York_road_transport",
              "alias": "New York"
            },
            {
              "name": "North_Carolina_road_transport",
              "alias": "North Carolina"
            },
            {
              "name": "North_Dakota_road_transport",
              "alias": "North Dakota"
            },
            {
              "name": "Ohio_road_transport",
              "alias": "Ohio"
            },
            {
              "name": "Oklahoma_road_transport",
              "alias": "Oklahoma"
            },
            {
              "name": "Oregon_road_transport",
              "alias": "Oregon"
            },
            {
              "name": "Pennsylvania_road_transport",
              "alias": "Pennsylvania"
            },
            {
              "name": "Puerto_Rico_road_transport",
              "alias": "Puerto Rico",
              "bgcolor": "silver"
            },
            {
              "name": "Rhode_Island_road_transport",
              "alias": "Rhode Island"
            },
            {
              "name": "South_Carolina_road_transport",
              "alias": "South Carolina"
            },
            {
              "name": "South_Dakota_road_transport",
              "alias": "South Dakota"
            },
            {
              "name": "Tennessee_road_transport",
              "alias": "Tennessee"
            },
            {
              "name": "Texas_road_transport",
              "alias": "Texas"
            },
            {
              "name": "U.S._Virgin_Islands_road_transport",
              "alias": "U.S. Virgin Islands",
              "bgcolor": "silver"
            },
            {
              "name": "Utah_road_transport",
              "alias": "Utah"
            },
            {
              "name": "Vermont_road_transport",
              "alias": "Vermont"
            },
            {
              "name": "Virginia_road_transport",
              "alias": "Virginia"
            },
            {
              "name": "Washington_road_transport",
              "alias": "Washington"
            },
            {
              "name": "West_Virginia_road_transport",
              "alias": "West Virginia"
            },
            {
              "name": "Wisconsin_road_transport",
              "alias": "Wisconsin"
            },
            {
              "name": "Wyoming_road_transport",
              "alias": "Wyoming"
            },
            {
              "name": "U.S._road_transport",
              "alias": "USRD",
              "bgcolor": "silver"
            }
          ],
          "categories": [
            "FA-Class",
            "A-Class",
            "GA-Class",
            "B-Class",
            "C-Class",
            "Start-Class",
            "Stub-Class"
          ]
        }',
        -- End of JSON params
        '2022-10-23T00:00:00Z', '2022-10-23T00:00:00Z', 1
    )
    ''', 'DELETE FROM custom WHERE c_name = "us_roads"')
]
