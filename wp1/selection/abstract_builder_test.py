from datetime import datetime
from unittest.mock import MagicMock, patch

from wp1.base_db_test import BaseWpOneDbTest
from wp1.models.wp10.builder import Builder
from wp1.models.wp10.selection import Selection
from wp1.selection.abstract_builder import AbstractBuilder


def _get_first_selection(wp10db):
  with wp10db.cursor() as cursor:
    cursor.execute('SELECT * from selections LIMIT 1')
    db_selection = cursor.fetchone()
    return Selection(**db_selection)


class TestBuilder(AbstractBuilder):

  def build(self, content_type, **params):
    return '\n'.join(params['list']).encode('utf-8')


class AbstractBuilderTest(BaseWpOneDbTest):

  def setUp(self):
    super().setUp()
    self.s3 = MagicMock()
    self.test_builder = TestBuilder()
    self.builder = Builder(b_id=100,
                           b_name=b'My Builder',
                           b_user_id=1234,
                           b_project=b'en.wikipedia.fake',
                           b_model=b'wp1.selection.models.simple',
                           b_params='{"list":["a","b","c"]}')

  def test_materialize_creates_selection(self):
    self.test_builder.materialize(self.s3, self.wp10db, self.builder,
                                  'text/tab-separated-values')
    actual = _get_first_selection(self.wp10db)
    self.assertEqual(actual.s_content_type, b'text/tab-separated-values')
    self.assertEqual(actual.s_builder_id, 100)

  @patch('wp1.models.wp10.selection.uuid.uuid4', return_value='abcd-1234')
  def test_materialize_selection_id(self, mock_uuid4):
    self.test_builder.materialize(self.s3, self.wp10db, self.builder,
                                  'text/tab-separated-values')
    actual = _get_first_selection(self.wp10db)
    self.assertEqual(actual.s_id, b'abcd-1234')

  @patch('wp1.models.wp10.selection.utcnow',
         return_value=datetime(2020, 12, 25, 10, 55, 44))
  def test_materialize_selection_updated_at(self, mock_utcnow):
    self.test_builder.materialize(self.s3, self.wp10db, self.builder,
                                  'text/tab-separated-values')
    actual = _get_first_selection(self.wp10db)
    self.assertEqual(actual.s_updated_at, b'20201225105544')

  @patch('wp1.models.wp10.selection.uuid.uuid4', return_value='abcd-1234')
  def test_materialize_uploads_to_s3(self, mock_uuid4):
    self.test_builder.materialize(self.s3, self.wp10db, self.builder,
                                  'text/tab-separated-values')
    data = self.s3.upload_fileobj.call_args[0][0]
    object_key = self.s3.upload_fileobj.call_args[1]['key']
    self.assertEqual(b'a\nb\nc', data.read())
    self.assertEqual('selections/wp1.selection.models.simple/abcd-1234.tsv',
                     object_key)
