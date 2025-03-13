import json
from unittest.mock import patch, MagicMock, ANY

from wp1.base_db_test import BaseWpOneDbTest
from wp1.custom_tables.us_roads import CustomTable as UsRoadsTable


class UsRoadsCustomTableTest(BaseWpOneDbTest):

  ratings = [(b'Apple', b'Art of testing', b'FA-Class'),
             (b'Apple', b'Testing mechanics', b'FA-Class'),
             (b'Banana', b'Rules of testing', b'FA-Class'),
             (b'Apple', b'Test practices', b'A-Class'),
             (b'Apple', b'Testing history', b'A-Class'),
             (b'Apple', b'Test frameworks', b'A-Class'),
             (b'Orange', b'Testing figures', b'A-Class'),
             (b'Orange', b'Important tests', b'A-Class'),
             (b'Orange', b'Test results', b'A-Class'),
             (b'Banana', b'Test main inheritance', b'A-Class'),
             (b'Apple', b'Test sub inheritance', b'Stub-Class'),
             (b'Apple', b'Test other inheritance', b'Stub-Class'),
             (b'Apple', b'Testing best practices', b'Stub-Class'),
             (b'Orange', b'Testing tools', b'Stub-Class'),
             (b'Orange', b'Operation of tests', b'Stub-Class'),
             (b'Banana', b'Lesser-known tests', b'Stub-Class'),
             (b'Banana', b'Failures of tests', b'Stub-Class'),
             (b'Banana', b'How to test', b'Stub-Class')]

  expected_wikicode = '''{|class="wikitable sortable"
|-
!Fruit
!{{FA-Class|category=Category:FA-Class Bar articles}}
!{{A-Class|category=Category:A-Class Bar articles}}
!{{Stub-Class|category=Category:Stub-Class Bar articles}}
!Total
!&#969;
!&#937;
|-
!bgcolor=red|[[User:WP_1.0_bot/Tables/Project/Apple|A]]
|bgcolor=red|2
|bgcolor=red|3
|bgcolor=red|3
|bgcolor=red|8
|bgcolor=red|9
|bgcolor=red|1.125
|-
!|[[User:WP_1.0_bot/Tables/Project/Orange|Orange]]
|0
|3
|2
|5
|7
|1.400
|-
!bgcolor=yellow|[[User:WP_1.0_bot/Tables/Project/Banana|Banana]]
|bgcolor=yellow|1
|bgcolor=yellow|1
|bgcolor=yellow|3
|bgcolor=yellow|5
|bgcolor=yellow|7
|bgcolor=yellow|1.400
|-
|}'''

  def setUp(self):
    super().setUp()
    with self.wp10db.cursor() as cursor:
      cursor.executemany(
          'INSERT INTO ratings (r_project, r_article, r_quality, r_namespace) VALUES (%s, %s, %s, 0)',
          self.ratings)

  def test_create_wikicode_golden(self):
    projects = [{
        'name': 'Apple',
        'bgcolor': 'red',
        'alias': 'A'
    }, {
        'name': 'Orange'
    }, {
        'name': 'Banana',
        'bgcolor': 'yellow'
    }]
    custom = UsRoadsTable(projects=projects,
                          categories=['FA-Class', 'A-Class', 'Stub-Class'],
                          parent_project='Bar',
                          aggregate_name='Fruit',
                          template='us_roads.jinja2')
    table_data = custom.generate(self.wp10db)
    actual = custom.create_wikicode(table_data)

    self.assertEqual(self.expected_wikicode, actual)
