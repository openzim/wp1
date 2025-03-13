from unittest.mock import patch, MagicMock

from wp1.base_db_test import BaseWpOneDbTest
from wp1.custom_tables.base_custom_table import BaseCustomTable


class BaseCustomTableTest(BaseWpOneDbTest):

  def test_generate_not_implemented(self):
    bct = BaseCustomTable()
    with self.assertRaises(NotImplementedError):
      bct.generate()

  def test_create_wikicode_not_implemented(self):
    bct = BaseCustomTable()
    with self.assertRaises(NotImplementedError):
      bct.create_wikicode()

  @patch('wp1.custom_tables.base_custom_table.api')
  def test_upload(self, patched_api):
    bct = BaseCustomTable()
    bct.generate = MagicMock()
    bct.create_wikicode = MagicMock()

    bct.upload(self.wp10db, b'foo', 'Wiki/Path')

    bct.generate.assert_called_once()
    bct.create_wikicode.assert_called_once()
    patched_api.get_page.assert_called_once_with(
        'User:WP 1.0 bot/Tables/Custom/Wiki/Path')
    patched_api.save_page.assert_called_once()
