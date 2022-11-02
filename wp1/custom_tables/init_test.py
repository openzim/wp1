import json
from unittest.mock import patch, MagicMock, ANY

from wp1.base_db_test import BaseWpOneDbTest
from wp1.custom_tables import all_custom_table_names, upload_custom_table_by_name


class CustomTablesInitTest(BaseWpOneDbTest):

  def test_all_custom_table_names(self):
    with self.wp10db.cursor() as cursor:
      cursor.execute('''
        INSERT INTO custom (c_name, c_module, c_is_active) VALUES
          ("Apple", "wp1.custom_tables.apple", 1),
          ("Orange", "wp1.custom_tables.apple", 0),
          ("Banana", "wp1.custom_tables.apple", 1)
      ''')

    actual = all_custom_table_names(self.wp10db)
    self.assertEqual([b'Apple', b'Banana'], actual)

  @patch('wp1.custom_tables.importlib')
  def test_upload_custom_table_by_name(self, patched_importlib):
    with self.wp10db.cursor() as cursor:
      cursor.execute('''
        INSERT INTO custom (c_name, c_module, c_params, c_is_active) VALUES
          ("foo", "wp1.custom_tables.foo", '{"wiki_path": "Wiki/Path"}', 1)
      ''')
    self.wp10db.commit()

    module = MagicMock()
    table_class = MagicMock()
    module.CustomTable.return_value = table_class
    patched_importlib.import_module.return_value = module

    orig_close = self.wp10db.close
    try:
      self.wp10db.close = lambda: True
      upload_custom_table_by_name(b'foo')
      module.CustomTable.assert_called_once()
      table_class.upload.assert_called_once_with(ANY, b'foo', 'Wiki/Path')
    finally:
      self.wp10db.close = orig_close

  @patch('wp1.custom_tables.importlib')
  def test_upload_custom_table_by_name_no_entry(self, patched_importlib):
    with self.wp10db.cursor() as cursor:
      cursor.execute('''
        INSERT INTO custom (c_name, c_module, c_params, c_is_active) VALUES
          ("foo", "wp1.custom_tables.foo", '{"wiki_path": "Wiki/Path"}', 1)
      ''')
    self.wp10db.commit()

    module = MagicMock()
    table_class = MagicMock()
    module.CustomTable.return_value = table_class
    patched_importlib.import_module.return_value = module

    orig_close = self.wp10db.close
    try:
      self.wp10db.close = lambda: True
      with self.assertRaises(ValueError):
        upload_custom_table_by_name(b'bar')
    finally:
      self.wp10db.close = orig_close

  @patch('wp1.custom_tables.importlib')
  def test_upload_custom_table_by_name_bad_json(self, patched_importlib):
    with self.wp10db.cursor() as cursor:
      cursor.execute('''
        INSERT INTO custom (c_name, c_module, c_params, c_is_active) VALUES
          ("foo", "wp1.custom_tables.foo", '{foo123}', 1)
      ''')
    self.wp10db.commit()

    module = MagicMock()
    table_class = MagicMock()
    module.CustomTable.return_value = table_class
    patched_importlib.import_module.return_value = module

    orig_close = self.wp10db.close
    try:
      self.wp10db.close = lambda: True
      with self.assertRaises(json.decoder.JSONDecodeError):
        upload_custom_table_by_name(b'foo')
    finally:
      self.wp10db.close = orig_close

  @patch('wp1.custom_tables.importlib')
  def test_upload_custom_table_by_name_bad_module_path(self, patched_importlib):
    with self.wp10db.cursor() as cursor:
      cursor.execute('''
        INSERT INTO custom (c_name, c_module, c_params, c_is_active) VALUES
          ("foo", "wp1.bar.foo", '{foo123}', 1)
      ''')
    self.wp10db.commit()

    module = MagicMock()
    table_class = MagicMock()
    module.CustomTable.return_value = table_class
    patched_importlib.import_module.return_value = module

    orig_close = self.wp10db.close
    try:
      self.wp10db.close = lambda: True
      with self.assertRaises(ValueError):
        upload_custom_table_by_name(b'foo')
    finally:
      self.wp10db.close = orig_close
