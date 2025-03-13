from datetime import datetime
import json
from unittest.mock import MagicMock, patch

from wp1.base_db_test import BaseWpOneDbTest, get_first_selection
from wp1.exceptions import Wp1RetryableSelectionError, Wp1FatalSelectionError, Wp1SelectionError
from wp1.models.wp10.builder import Builder
from wp1.models.wp10.selection import Selection
from wp1.selection.abstract_builder import AbstractBuilder


class TestBuilder(AbstractBuilder):

  def build(self, content_type, **params):
    return '\n'.join(params['list']).encode('utf-8')


class TestBuilderRetryable(AbstractBuilder):

  def build(self, content_type, **params):
    try:
      int('Not an int')
    except ValueError as e:
      raise Wp1RetryableSelectionError('Could not convert to int') from e


class TestBuilderFatal(AbstractBuilder):

  def build(self, content_type, **params):
    try:
      int('Not an int')
    except ValueError as e:
      raise Wp1FatalSelectionError('Could not convert to int') from e


class TestBuilderNoContext(AbstractBuilder):

  def build(self, content_type, **params):
    raise Wp1FatalSelectionError('Something broke')


class TestBuilderSuppressedException(AbstractBuilder):

  def build(self, content_type, **params):
    try:
      int('Not an int')
    except ValueError as e:
      raise Wp1SelectionError('Just this thing, really') from None


class AbstractBuilderTest(BaseWpOneDbTest):

  def setUp(self):
    super().setUp()
    self.s3 = MagicMock()
    self.test_builder = TestBuilder()
    self.builder = Builder(b_id=b'1a-2b-3c-4d',
                           b_name=b'My Builder',
                           b_user_id=1234,
                           b_project=b'en.wikipedia.fake',
                           b_model=b'wp1.selection.models.fake',
                           b_params='{"list":["a","b","c"]}')

  def test_materialize_creates_selection(self):
    self.test_builder.materialize(self.s3, self.wp10db, self.builder,
                                  'text/tab-separated-values', 1)

    actual = get_first_selection(self.wp10db)

    self.assertEqual(actual.s_content_type, b'text/tab-separated-values')
    self.assertEqual(actual.s_builder_id, b'1a-2b-3c-4d')

  @patch('wp1.models.wp10.selection.uuid.uuid4', return_value='abcd-1234')
  def test_materialize_selection_id(self, mock_uuid4):
    self.test_builder.materialize(self.s3, self.wp10db, self.builder,
                                  'text/tab-separated-values', 1)

    actual = get_first_selection(self.wp10db)

    self.assertEqual(actual.s_id, b'abcd-1234')

  @patch('wp1.models.wp10.selection.uuid.uuid4', return_value='abcd-1234')
  def test_materialize_selection_object_key(self, mock_uuid4):
    self.test_builder.materialize(self.s3, self.wp10db, self.builder,
                                  'text/tab-separated-values', 1)

    actual = get_first_selection(self.wp10db)

    self.assertEqual(
        actual.s_object_key, b'selections/wp1.selection.models.fake/'
        b'abcd-1234/MyBuilder.tsv')

  @patch('wp1.models.wp10.selection.utcnow',
         return_value=datetime(2020, 12, 25, 10, 55, 44))
  def test_materialize_selection_updated_at(self, mock_utcnow):
    self.test_builder.materialize(self.s3, self.wp10db, self.builder,
                                  'text/tab-separated-values', 1)

    actual = get_first_selection(self.wp10db)

    self.assertEqual(actual.s_updated_at, b'20201225105544')

  @patch('wp1.models.wp10.selection.uuid.uuid4', return_value='abcd-1234')
  def test_materialize_uploads_to_s3(self, mock_uuid4):
    self.test_builder.materialize(self.s3, self.wp10db, self.builder,
                                  'text/tab-separated-values', 1)

    data = self.s3.upload_fileobj.call_args[0][0]
    object_key = self.s3.upload_fileobj.call_args[1]['key']
    self.assertEqual(b'a\nb\nc', data.read())
    self.assertEqual(
        'selections/wp1.selection.models.fake/abcd-1234/MyBuilder.tsv',
        object_key)

  def test_materialize_version(self):
    self.test_builder.materialize(self.s3, self.wp10db, self.builder,
                                  'text/tab-separated-values', 5)

    actual = get_first_selection(self.wp10db)

    self.assertEqual(5, actual.s_version)

  def test_materialize_retryable_error(self):
    builder_obj = TestBuilderRetryable()
    builder_obj.materialize(self.s3, self.wp10db, self.builder,
                            'text/tab-separated-values', 1)

    actual = get_first_selection(self.wp10db)

    self.assertEqual(b'CAN_RETRY', actual.s_status)

  def test_materialize_retryable_error_messages(self):
    builder_obj = TestBuilderRetryable()
    builder_obj.materialize(self.s3, self.wp10db, self.builder,
                            'text/tab-separated-values', 1)

    actual = get_first_selection(self.wp10db)

    self.assertEqual(
        {
            'error_messages': [
                'Could not convert to int',
                "invalid literal for int() with base 10: 'Not an int'"
            ]
        }, json.loads(actual.s_error_messages))

  def test_materialize_fatal_error(self):
    builder_obj = TestBuilderFatal()
    builder_obj.materialize(self.s3, self.wp10db, self.builder,
                            'text/tab-separated-values', 1)

    actual = get_first_selection(self.wp10db)

    self.assertEqual(b'FAILED', actual.s_status)

  def test_materialize_fatal_error_messages(self):
    builder_obj = TestBuilderFatal()
    builder_obj.materialize(self.s3, self.wp10db, self.builder,
                            'text/tab-separated-values', 1)

    actual = get_first_selection(self.wp10db)

    self.assertEqual(
        {
            'error_messages': [
                'Could not convert to int',
                "invalid literal for int() with base 10: 'Not an int'"
            ]
        }, json.loads(actual.s_error_messages))

  def test_materialize_no_context_messages(self):
    builder_obj = TestBuilderNoContext()
    builder_obj.materialize(self.s3, self.wp10db, self.builder,
                            'text/tab-separated-values', 1)

    actual = get_first_selection(self.wp10db)

    self.assertEqual({'error_messages': ['Something broke']},
                     json.loads(actual.s_error_messages))

  def test_materialize_suppressed_message(self):
    builder_obj = TestBuilderSuppressedException()
    builder_obj.materialize(self.s3, self.wp10db, self.builder,
                            'text/tab-separated-values', 1)

    actual = get_first_selection(self.wp10db)

    self.assertEqual({'error_messages': ['Just this thing, really']},
                     json.loads(actual.s_error_messages))
