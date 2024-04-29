import unittest
from unittest.mock import MagicMock

from wp1.base_db_test import BaseWpOneDbTest, get_first_selection
from wp1.exceptions import Wp1FatalSelectionError, Wp1RetryableSelectionError
from wp1.models.wp10.builder import Builder
from wp1.selection.models.simple import Builder as SimpleBuilder


class SimpleBuilderTest(BaseWpOneDbTest):
  valid_items = [
      'Eiffel_Tower     ',
      'Statue of Liberty',
      'https://en.wikipedia.org/wiki/Liberty_(personification)',
      'https://en.wikipedia.org/w/index.php?title=Libertas',
      'https://en.wikipedia.org/w/index.php?title=%E2%88%9E',
      'George-%C3%89tienne_Cartier_Monument',
  ]

  invalid_items = [
      'This is supposedly an article \
name but its way too long to actually be \
one because it contains more than 256 characters \
which is not allowed in article titles and \
it just runs on forever, it doesnt even have \
underscores and looks more like a long paragraph \
of text than an actual article name.',
      'Not_an_<article_name>',
      'https://en.wikipedia.org/wiki/Liberty#Philosophy',
  ]

  params = {
      'list': [
          *valid_items,
          *invalid_items,
      ]
  }

  def setUp(self):
    super().setUp()
    self.s3 = MagicMock()
    self.builder = Builder(b_id=b'1a-2b-3c-4d',
                           b_name=b'Simple Builder',
                           b_user_id=1234,
                           b_project=b'en.wikipedia.fake',
                           b_model=b'wp1.selection.models.simple',
                           b_params='{"list":["a","b","c"]}')

  def test_materialize(self):
    simple_test_builder = SimpleBuilder()
    simple_test_builder.materialize(self.s3, self.wp10db, self.builder,
                                    'text/tab-separated-values', 1)
    actual = get_first_selection(self.wp10db)
    self.assertEqual(actual.s_content_type, b'text/tab-separated-values')
    self.assertEqual(actual.s_builder_id, b'1a-2b-3c-4d')

  def test_build(self):
    simple_test_builder = SimpleBuilder()
    params = {'list': ['Eiffel_Tower', 'Statue of Liberty', 'Libertas']}
    actual = simple_test_builder.build('text/tab-separated-values', **params)
    self.assertEqual(b'Eiffel_Tower\nStatue_of_Liberty\nLibertas', actual)

  def test_build_unrecognized_content_type(self):
    simple_test_builder = SimpleBuilder()
    with self.assertRaises(Wp1FatalSelectionError):
      simple_test_builder.build('invalid_content_type', **self.params)

  def test_build_incorrect_params(self):
    simple_test_builder = SimpleBuilder()
    params = {'items': ['Eiffel_Tower', 'Statue of Liberty', 'Libertas']}
    with self.assertRaises(Wp1FatalSelectionError):
      simple_test_builder.build('text/tab-separated-values', **params)

  def test_build_ignores_unwanted_params(self):
    simple_test_builder = SimpleBuilder()
    params = {
        'list': ['Eiffel_Tower', 'Statue of Liberty', 'Libertas'],
        'project': 'project_name'
    }
    actual = simple_test_builder.build('text/tab-separated-values', **params)
    self.assertEqual(b'Eiffel_Tower\nStatue_of_Liberty\nLibertas', actual)

  def test_build_ignores_comments(self):
    simple_test_builder = SimpleBuilder()
    expected = b'Eiffel_Tower\nStatue_of_Liberty\nLiberty_(personification)'
    params = {
        'list': [
            '# Starting with a comment', '\n', 'Eiffel_Tower', '# Comment here',
            '# Consecutive comments', 'Statue_of_Liberty',
            '###Comment with lots of #', 'Liberty_(personification)',
            '#Ending with a comment#'
        ]
    }
    actual = simple_test_builder.build('text/tab-separated-values', **params)
    self.assertEqual(expected, actual)

  def test_build_ignores_whitespace(self):
    simple_test_builder = SimpleBuilder()
    expected = b'Eiffel_Tower\nStatue_of_Liberty\nLiberty_(personification)'
    params = {
        'list': [
            '\n', '  Eiffel_Tower', '\n\t  \n  \t', 'Statue_of_Liberty  ',
            '   ', 'Liberty_(personification)', '\n\n\n'
        ],
    }
    actual = simple_test_builder.build('text/tab-separated-values', **params)
    self.assertEqual(expected, actual)

  def test_build_decodes_utf8_and_url_encoding(self):
    simple_test_builder = SimpleBuilder()
    expected = '\n'.join([
        'Eiffel_Tower', 'Statue_of_Liberty', 'Liberty_(personification)',
        'Libertas', '∞', 'George-Étienne_Cartier_Monument'
    ]).encode('utf-8')
    actual = simple_test_builder.build('text/tab-separated-values',
                                       list=self.valid_items)
    self.assertEqual(expected, actual)

  def test_build_disallows_invalid(self):
    simple_test_builder = SimpleBuilder()
    with self.assertRaises(Wp1RetryableSelectionError):
      simple_test_builder.build('text/tab-separated-values', list=['Foo#Bar'])

  def test_validate_items(self):
    simple_builder_test = SimpleBuilder()
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
    ], [
        'The list contained an item longer than 256 bytes',
        'The list contained the following invalid characters: <, >, #'
    ])
    actual = simple_builder_test.validate(**self.params)
    self.assertEqual(expected, actual)

  def test_validate_empty_items(self):
    simple_test_builder = SimpleBuilder()
    params = {'list': []}
    actual = simple_test_builder.validate(**params)
    self.assertEqual(([], [], ['Empty List']), actual)

  def test_validate_whitespace_lines_ignored(self):
    simple_builder_test = SimpleBuilder()
    expected = ([
        'Eiffel_Tower', 'Statue_of_Liberty', 'Liberty_(personification)'
    ], [], [])
    params = {
        'list': [
            '\n', '  Eiffel_Tower', '\n\t  \n  \t', 'Statue_of_Liberty  ',
            '   ', 'Liberty_(personification)', '\n\n\n'
        ],
        'project': 'project_name'
    }
    actual = simple_builder_test.validate(**params)
    self.assertEqual(expected, actual)

  def test_validate_comments_ignored(self):
    simple_builder_test = SimpleBuilder()
    expected = ([
        'Eiffel_Tower', 'Statue_of_Liberty', 'Liberty_(personification)'
    ], [], [])
    params = {
        'list': [
            '# Starting with a comment', '\n', 'Eiffel_Tower', '# Comment here',
            '# Consecutive comments', 'Statue_of_Liberty',
            '###Comment with lots of #', 'Liberty_(personification)',
            '#Ending with a comment#'
        ],
        'project': 'project_name'
    }
    actual = simple_builder_test.validate(**params)
    self.assertEqual(expected, actual)

  def test_validate_max_size(self):
    simple_builder_test = SimpleBuilder()
    expected = ([], [],
                ['The list was longer than %s' % SimpleBuilder.MAX_LIST_DESC])
    junk_list = []
    for _ in range(SimpleBuilder.MAX_LIST_SIZE // 10 + 1):
      junk_list.append('abcdefghij0123456789')
    params = {
        'list': junk_list,
        'project': 'project_name',
    }
    actual = simple_builder_test.validate(**params)
    self.assertEqual(expected, actual)
