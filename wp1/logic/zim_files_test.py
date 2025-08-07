from wp1.base_db_test import BaseWpOneDbTest
from wp1.logic.zim_files import get_zim_file
from wp1.models.wp10.zim_file import ZimFile


class ZimFilesTest(BaseWpOneDbTest):

    def setUp(self):
        super().setUp()
        self.test_zim_file_id = 1234 
        self.test_zim_file_data = {
            'z_id': self.test_zim_file_id,
            'z_selection_id': b'test-selection-id',
            'z_status': b'COMPLETED',
            'z_task_id': b'test-task-id',
            'z_requested_at': None,
            'z_updated_at': None,
            'z_long_description': b'Test long description',
            'z_description': b'Test description',
            'z_title': b'Test ZIM File Title'
        }

    def test_get_zim_file(self):
        """Test successful retrieval of a ZIM file."""
        with self.wp10db.cursor() as cursor:
            cursor.execute('''
                INSERT INTO zim_files (
                    z_id, z_selection_id, z_status, z_task_id, z_requested_at,
                    z_updated_at, z_long_description, z_description, z_title
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                self.test_zim_file_data['z_id'],
                self.test_zim_file_data['z_selection_id'],
                self.test_zim_file_data['z_status'],
                self.test_zim_file_data['z_task_id'],
                self.test_zim_file_data['z_requested_at'],
                self.test_zim_file_data['z_updated_at'],
                self.test_zim_file_data['z_long_description'],
                self.test_zim_file_data['z_description'],
                self.test_zim_file_data['z_title']
            ))
        
        result = get_zim_file(self.wp10db, self.test_zim_file_id)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ZimFile)
        self.assertEqual(result.z_id, self.test_zim_file_id)
        self.assertEqual(result.z_selection_id, self.test_zim_file_data['z_selection_id'])
        self.assertEqual(result.z_status, self.test_zim_file_data['z_status'])
        self.assertEqual(result.z_task_id, self.test_zim_file_data['z_task_id'])
        self.assertEqual(result.z_title, self.test_zim_file_data['z_title'])
        self.assertEqual(result.z_description, self.test_zim_file_data['z_description'])
        self.assertEqual(result.z_long_description, self.test_zim_file_data['z_long_description'])

    def test_get_zim_file_not_found(self):
        """Test retrieval of a non-existent ZIM file."""
        non_existent_id = b'non-existent-id'
        result = get_zim_file(self.wp10db, non_existent_id)
        self.assertIsNone(result)

    def test_get_zim_file_with_null_fields(self):
        """Test retrieval of a ZIM file with some null fields."""
        zim_file_data_with_nulls = {
            'z_id': 1234,
            'z_selection_id': b'test-selection-id-2',
            'z_status': b'IN_PROGRESS',
            'z_task_id': None,  # Null task_id
            'z_requested_at': None,
            'z_updated_at': None,
            'z_long_description': None,  # Null long description
            'z_description': None,  # Null description
            'z_title': None  # Null title
        }
        
        with self.wp10db.cursor() as cursor:
            cursor.execute('''
                INSERT INTO zim_files (
                    z_id, z_selection_id, z_status, z_task_id, z_requested_at,
                    z_updated_at, z_long_description, z_description, z_title
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                zim_file_data_with_nulls['z_id'],
                zim_file_data_with_nulls['z_selection_id'],
                zim_file_data_with_nulls['z_status'],
                zim_file_data_with_nulls['z_task_id'],
                zim_file_data_with_nulls['z_requested_at'],
                zim_file_data_with_nulls['z_updated_at'],
                zim_file_data_with_nulls['z_long_description'],
                zim_file_data_with_nulls['z_description'],
                zim_file_data_with_nulls['z_title']
            ))
        
        result = get_zim_file(self.wp10db, zim_file_data_with_nulls['z_id'])
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ZimFile)
        self.assertEqual(result.z_id, zim_file_data_with_nulls['z_id'])
        self.assertEqual(result.z_selection_id, zim_file_data_with_nulls['z_selection_id'])
        self.assertEqual(result.z_status, zim_file_data_with_nulls['z_status'])
        self.assertIsNone(result.z_task_id)
        self.assertIsNone(result.z_title)
        self.assertIsNone(result.z_description)
        self.assertIsNone(result.z_long_description)

    def test_get_zim_file_multiple_records(self):
        """Test that get_zim_file returns the correct record when multiple exist."""
        zim_file_1_data = {
            'z_id': 1234,
            'z_selection_id': b'test-selection-1',
            'z_status': b'COMPLETED',
            'z_task_id': b'test-task-1',
            'z_requested_at': None,
            'z_updated_at': None,
            'z_long_description': b'Test long description 1',
            'z_description': b'Test description 1',
            'z_title': b'Test ZIM File 1'
        }
        zim_file_2_data = {
            'z_id': 4321,
            'z_selection_id': b'test-selection-2',
            'z_status': b'IN_PROGRESS',
            'z_task_id': b'test-task-2',
            'z_requested_at': None,
            'z_updated_at': None,
            'z_long_description': b'Test long description 2',
            'z_description': b'Test description 2',
            'z_title': b'Test ZIM File 2'
        }
        
        with self.wp10db.cursor() as cursor:
            # Insert first record
            cursor.execute('''
                INSERT INTO zim_files (
                    z_id, z_selection_id, z_status, z_task_id, z_requested_at,
                    z_updated_at, z_long_description, z_description, z_title
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', tuple(zim_file_1_data.values()))
            
            # Insert second record
            cursor.execute('''
                INSERT INTO zim_files (
                    z_id, z_selection_id, z_status, z_task_id, z_requested_at,
                    z_updated_at, z_long_description, z_description, z_title
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', tuple(zim_file_2_data.values()))
        
        result_1 = get_zim_file(self.wp10db, zim_file_1_data['z_id'])
        self.assertIsNotNone(result_1)
        self.assertEqual(result_1.z_id, zim_file_1_data['z_id'])
        self.assertEqual(result_1.z_title, zim_file_1_data['z_title'])
        
        result_2 = get_zim_file(self.wp10db, zim_file_2_data['z_id'])
        self.assertIsNotNone(result_2)
        self.assertEqual(result_2.z_id, zim_file_2_data['z_id'])
        self.assertEqual(result_2.z_title, zim_file_2_data['z_title'])
