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
              '1a-2b-3c-4d',
          'name':
              'name',
          'project':
              'project_name',
          'created_at':
              1608893744,
          'updated_at':
              1608893744,
          'model':
              'model',
          's_id':
              '1',
          's_updated_at':
              1608893744,
          's_content_type':
              'text/tab-separated-values',
          's_extension':
              'tsv',
          's_url':
              'http://test.server.fake/v1/builders/1a-2b-3c-4d/selection/latest.tsv',
          's_status':
              'OK',
          's_zim_file_updated_at':
              None,
          's_zim_file_url':
              None,
          's_zimfarm_status':
              'NOT_REQUESTED',
      }],
  }

  expected_lists_with_multiple_selections = {
      'builders': [
          {
              'id':
                  '1a-2b-3c-4d',
              'name':
                  'name',
              'project':
                  'project_name',
              'created_at':
                  1608893744,
              'updated_at':
                  1608893744,
              'model':
                  'model',
              's_id':
                  '2',
              's_updated_at':
                  1608893744,
              's_content_type':
                  'application/vnd.ms-excel',
              's_extension':
                  'xls',
              's_url':
                  'http://test.server.fake/v1/builders/1a-2b-3c-4d/selection/latest.xls',
              's_status':
                  None,
              's_zim_file_updated_at':
                  None,
              's_zim_file_url':
                  None,
              's_zimfarm_status':
                  'NOT_REQUESTED',
          },
          {
              'id': '1a-2b-3c-4d',
              'name': 'name',
              'project': 'project_name',
              'created_at': 1608893744,
              'updated_at': 1608893744,
              'model': 'model',
              's_id': '1',
              's_updated_at': 1608893744,
              's_content_type': 'text/tab-separated-values',
              's_extension': 'tsv',
              's_url': None,
              's_status': 'CAN_RETRY',
              's_zim_file_updated_at': None,
              's_zim_file_url': None,
              's_zimfarm_status': 'NOT_REQUESTED',
          },
      ]
  }

  expected_lists_with_no_selections = {
      'builders': [{
          'id': '1a-2b-3c-4d',
          'name': 'name',
          'project': 'project_name',
          'model': 'model',
          'created_at': 1608893744,
          'updated_at': 1608893744,
          's_id': None,
          's_updated_at': None,
          's_content_type': None,
          's_extension': None,
          's_url': None,
          's_status': None,
          's_zim_file_updated_at': None,
          's_zim_file_url': None,
          's_zimfarm_status': None,
      }]
  }

  def test_get_list_data(self):
    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with self.wp10db.cursor() as cursor:
        cursor.execute('''
          INSERT INTO builders
            (b_id, b_name, b_user_id, b_project, b_model, b_created_at, b_updated_at, b_current_version)
          VALUES
            ('1a-2b-3c-4d', 'name', '1234', 'project_name', 'model', '20201225105544', '20201225105544', 1)
        ''')
        cursor.execute('''
            INSERT INTO selections
              (s_id, s_builder_id, s_content_type, s_updated_at, s_version, s_object_key)
            VALUES
              (1, \'1a-2b-3c-4d\', "text/tab-separated-values", "20201225105544", 1, "object_key")
        ''')
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
        (b_id, b_name, b_user_id, b_project, b_model, b_created_at, b_updated_at, b_current_version)
        VALUES ('1a-2b-3c-4d', 'name', '1234', 'project_name', 'model', '20201225105544', '20201225105544', 1)
      ''')
        cursor.execute('''
            INSERT INTO selections
              (s_id, s_builder_id, s_content_type, s_updated_at, s_version, s_object_key,
               s_status, s_error_messages)
            VALUES
              (1, \'1a-2b-3c-4d\', "text/tab-separated-values", "20201225105544", 1,
               "object_key_1", "CAN_RETRY", \'{"errors"["error1"]}\')
        ''')
        cursor.execute('''
            INSERT INTO selections
              (s_id, s_builder_id, s_content_type, s_updated_at, s_version, s_object_key,
               s_status, s_error_messages, s_zimfarm_status)
            VALUES
              (2, \'1a-2b-3c-4d\', "application/vnd.ms-excel", "20201225105544", 1,
               "object_key_2", NULL, NULL, 'NOT_REQUESTED')
        ''')
      self.wp10db.commit()
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.get('/v1/selection/simple/lists')
      self.assertObjectListsEqual(
          self.expected_lists_with_multiple_selections['builders'],
          rv.get_json()['builders'])

  def test_list_with_no_selections(self):
    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with self.wp10db.cursor() as cursor:
        cursor.execute('''INSERT INTO builders
        (b_id, b_name, b_user_id, b_project, b_model, b_created_at, b_updated_at, b_current_version)
        VALUES ('1a-2b-3c-4d', 'name', '1234', 'project_name', 'model', '20201225105544', '20201225105544', 1)
      ''')
      self.wp10db.commit()
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.get('/v1/selection/simple/lists')
      self.assertObjectListsEqual(
          self.expected_lists_with_no_selections['builders'],
          rv.get_json()['builders'])

  def test_list_with_no_builders(self):
    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      with self.wp10db.cursor() as cursor:
        cursor.execute('''
          INSERT INTO selections
            (s_id, s_builder_id, s_content_type, s_updated_at, s_version, s_object_key)
          VALUES
            (2, \'1a-2b-3c-4d\', "application/vnd.ms-excel", '20201225105544', 1, "object_key")
        ''')
      self.wp10db.commit()
      with client.session_transaction() as sess:
        sess['user'] = self.USER
      rv = client.get('/v1/selection/simple/lists')
      self.assertEqual({'builders': []}, rv.get_json())
