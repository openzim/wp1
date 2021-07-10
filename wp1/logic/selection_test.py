from datetime import datetime
import unittest
from unittest.mock import patch

from wp1.base_db_test import BaseWpOneDbTest, get_storage_mock
from wp1.logic import selection as logic_selection
from wp1.models.wp10.selection import Selection


class ValidateArticleNameTest(unittest.TestCase):

  items = '''Eiffel_Tower
Statue of Liberty
This is supposedly an article \
name but its way too long to actually be \
one because it contains more than 256 characters \
which is not allowed in article titles and \
it just runs on forever, it doesnt even have \
underscores and looks more like a long paragraph \
of text than an actual article name.
Not_an_<article_name>
https://en.wikipedia.org/wiki/Liberty#Philosophy
https://en.wikipedia.org/wiki/Liberty_(personification)
https://en.wikipedia.org/w/index.php?title=Libertas
https://en.wikipedia.org/w/index.php?title=%E2%88%9E
George-%C3%89tienne_Cartier_Monument'''

  def test_validate_items(self):
    expected = ([
        'Eiffel_Tower', 'Statue_of_Liberty', 'Liberty_(personification)',
        'Libertas', '∞', 'George-Étienne_Cartier_Monument'
    ], [
        'This_is_supposedly_an_article_name_but_'
        'its_way_too_long_to_actually_be_one_'
        'because_it_contains_more_than_256_characters'
        '_which_is_not_allowed_in_article_titles_and_'
        'it_just_runs_on_forever,_it_doesnt_even_have_'
        'underscores_and_looks_more_like_a_long_paragraph'
        '_of_text_than_an_actual_article_name.', 'Not_an_<article_name>',
        'https://en.wikipedia.org/wiki/Liberty#Philosophy'
    ], ['length greater than 256 bytes', '<', '>', '#'])
    actual = logic_selection.validate_list(self.items)
    self.assertEqual(expected, actual)


class PersistSelectionTest(BaseWpOneDbTest):

  def get_first_selection(self):
    with self.wp10db.cursor() as cursor:
      cursor.execute('SELECT * FROM selections LIMIT 1')
      db_selection = cursor.fetchone()
      return Selection(**db_selection) if db_selection else None

  def setUp(self):
    super().setUp()
    self.s3_mock = get_storage_mock()

    self.selection = Selection(b'Test name',
                               1234,
                               'en.wikipedia.org.fake',
                               s_object_key=b'selections/1234/abcd.tsv')
    self.selection.data = b'Article_1\nArticle_2'
    self.persist_args = [
        self.wp10db, self.s3_mock, 'Test name', '1234', 'en.wikipedia.org.fake',
        ['Article_1', 'Article_2']
    ]

  def test_upload_to_calls_upload(self):
    logic_selection._upload_to_storage(self.s3_mock, self.selection)

    self.s3_mock.upload_fileobj.assert_called_once()

  def test_upload_to_storage_data_seeked_to_0(self):
    logic_selection._upload_to_storage(self.s3_mock, self.selection)

    args = self.s3_mock.upload_fileobj.call_args
    data_io = args[0][0]
    self.assertEqual(0, data_io.tell())

  def test_upload_to_storage_data_equal(self):
    logic_selection._upload_to_storage(self.s3_mock, self.selection)

    args = self.s3_mock.upload_fileobj.call_args
    data_io = args[0][0]
    self.assertEqual(b'Article_1\nArticle_2', data_io.read())

  def test_upload_to_storage_key_equal(self):
    logic_selection._upload_to_storage(self.s3_mock, self.selection)

    args = self.s3_mock.upload_fileobj.call_args
    key = args[1]['key']
    self.assertEqual('selections/1234/abcd.tsv', key)

  @patch('wp1.models.wp10.selection.utcnow',
         return_value=datetime(2018, 12, 25, 5, 55, 55))
  def test_persist_simple_list_sets_last_generated(self, mock_utcnow):
    logic_selection.persist_simple_list(*self.persist_args)
    actual = self.get_first_selection()
    self.assertEqual(b'2018-12-25T05:55:55Z', actual.s_last_generated)

  @patch('wp1.models.wp10.selection.utcnow',
         return_value=datetime(2018, 12, 25, 5, 55, 55))
  def test_persist_simple_list_sets_created_at(self, mock_utcnow):
    logic_selection.persist_simple_list(*self.persist_args)
    actual = self.get_first_selection()
    self.assertEqual(b'2018-12-25T05:55:55Z', actual.s_created_at)

  def test_persist_simple_list_sets_user_id(self):
    logic_selection.persist_simple_list(*self.persist_args)
    actual = self.get_first_selection()
    self.assertEqual(1234, actual.s_user_id)

  def test_persist_simple_list_sets_name(self):
    logic_selection.persist_simple_list(*self.persist_args)
    actual = self.get_first_selection()
    self.assertEqual(b'Test name', actual.s_name)

  def test_persist_simple_list_sets_project(self):
    logic_selection.persist_simple_list(*self.persist_args)
    actual = self.get_first_selection()
    self.assertEqual(b'en.wikipedia.org.fake', actual.s_project)

  def test_persist_simple_list_sets_hash(self):
    logic_selection.persist_simple_list(*self.persist_args)
    actual = self.get_first_selection()
    self.assertIsNotNone(actual.s_hash)

  def test_persist_simple_list_sets_object_key(self):
    logic_selection.persist_simple_list(*self.persist_args)
    actual = self.get_first_selection()
    expected_object_key = b'selections/org.openzim.wp1.simple/1234/%s.tsv' % actual.s_hash
    self.assertEqual(expected_object_key, actual.s_object_key)

  def test_persist_simple_list_sets_model(self):
    logic_selection.persist_simple_list(*self.persist_args)
    actual = self.get_first_selection()
    self.assertEqual(b'org.openzim.wp1.simple', actual.s_model)

  def test_persist_simple_list_sets_region(self):
    logic_selection.persist_simple_list(*self.persist_args)
    actual = self.get_first_selection()
    self.assertEqual(b'test-region', actual.s_region)

  def test_persist_simple_list_sets_bucket(self):
    logic_selection.persist_simple_list(*self.persist_args)
    actual = self.get_first_selection()
    self.assertEqual(b'test-bucket-name', actual.s_bucket)
