from unittest.mock import patch
from wp1.web.app import create_app
from wp1.web.base_web_testcase import BaseWebTestcase


class SelectionTest(BaseWebTestcase):
  USER = {
      'access_token': 'access_token',
      'identity': {
          'username': 'WP1_user',
          'sub': '1234',
      },
  }

  expected_list_data = {
      'builders': [{
          'id':
              1,
          'name':
              'name',
          'project':
              'project_name',
          'selections': [{
              'id': '1',
              'content_type': 'text/tab-separated-values',
              'extension': 'tsv',
              'url': 'http://credentials.not.found.fake/selections/model/1.tsv'
          }],
      }],
  }

  expected_lists_with_multiple_selections = {
      'builders': [{
          'id':
              1,
          'name':
              'name',
          'project':
              'project_name',
          'selections': [{
              'id': '1',
              'content_type': 'text/tab-separated-values',
              'extension': 'tsv',
              'url': 'http://credentials.not.found.fake/selections/model/1.tsv'
          }, {
              'id': '2',
              'content_type': 'application/vnd.ms-excel',
              'extension': 'xls',
              'url': 'http://credentials.not.found.fake/selections/model/2.xls'
          }]
      }]
  }

  expected_lists_with_no_selections = {
      'builders': [{
          'id': 1,
          'name': 'name',
          'project': 'project_name',
          'selections': []
      }]
  }

  def test_get_list_data(self):
    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with self.wp10db.cursor() as cursor:
        cursor.execute('''INSERT INTO builders
        (b_name, b_user_id, b_project, b_model)
        VALUES ('name', '1234', 'project_name', 'model')
      ''')
        cursor.execute(
            'INSERT INTO selections VALUES (1, 1, "text/tab-separated-values", "20201225105544")'
        )
      self.wp10db.commit()
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.get('/v1/selection/simple/lists')
      self.assertEqual(self.expected_list_data, rv.get_json())

  def test_list_with_multiple_selections(self):
    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with self.wp10db.cursor() as cursor:
        cursor.execute('''INSERT INTO builders
        (b_name, b_user_id, b_project, b_model)
        VALUES ('name', '1234', 'project_name', 'model')
      ''')
        cursor.execute(
            'INSERT INTO selections VALUES (1, 1, "text/tab-separated-values", "20201225105544")'
        )
        cursor.execute(
            'INSERT INTO selections VALUES (2, 1, "application/vnd.ms-excel", "20201225105544")'
        )
      self.wp10db.commit()
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.get('/v1/selection/simple/lists')
      self.assertEqual(self.expected_lists_with_multiple_selections,
                       rv.get_json())

  def test_list_with_no_selections(self):
    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with self.wp10db.cursor() as cursor:
        cursor.execute('''INSERT INTO builders
        (b_name, b_user_id, b_project, b_model)
        VALUES ('name', '1234', 'project_name', 'model')
      ''')
      self.wp10db.commit()
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.get('/v1/selection/simple/lists')
      self.assertEqual(self.expected_lists_with_no_selections, rv.get_json())

  def test_list_with_no_builders(self):
    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with self.wp10db.cursor() as cursor:
        cursor.execute(
            '''INSERT INTO selections VALUES (2, 1, "application/vnd.ms-excel", '20201225105544')'''
        )
      self.wp10db.commit()
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.get('/v1/selection/simple/lists')
      self.assertEqual({'builders': []}, rv.get_json())
