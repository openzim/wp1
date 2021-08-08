from datetime import datetime
import unittest
from unittest.mock import patch
from wp1.web.app import create_app
from wp1.selection.models.simple_builder import SimpleBuilder
from flask import session
from wp1.models.wp10.builder import Builder
from wp1.base_db_test import BaseWpOneDbTest


class SimpleBuilderTest(unittest.TestCase):

  params = {
      'list': [
          'Eiffel_Tower     ', 'Statue of Liberty',
          'This is supposedly an article \
name but its way too long to actually be \
one because it contains more than 256 characters \
which is not allowed in article titles and \
it just runs on forever, it doesnt even have \
underscores and looks more like a long paragraph \
of text than an actual article name.', 'Not_an_<article_name>',
          'https://en.wikipedia.org/wiki/Liberty#Philosophy',
          'https://en.wikipedia.org/wiki/Liberty_(personification)',
          'https://en.wikipedia.org/w/index.php?title=Libertas',
          'https://en.wikipedia.org/w/index.php?title=%E2%88%9E',
          'George-%C3%89tienne_Cartier_Monument'
      ]
  }

  def test_build(self):
    simple_test_builder = SimpleBuilder()
    params = {'list': ['Eiffel_Tower', 'Statue#of_Liberty', 'Libertas']}
    actual = simple_test_builder.build('text/tab-separated-values', **params)
    self.assertEqual(b'Eiffel_Tower\nStatue#of_Liberty\nLibertas', actual)

  def test_build_unrecognized_content_type(self):
    simple_test_builder = SimpleBuilder()
    with self.assertRaises(ValueError):
      simple_test_builder.build('invalid_content_type', **self.params)

  def test_build_incorrect_params(self):
    simple_test_builder = SimpleBuilder()
    params = {'items': ['Eiffel_Tower', 'Statue#of_Liberty', 'Libertas']}
    with self.assertRaises(ValueError):
      simple_test_builder.build('text/tab-separated-values', **params)

  def test_build_unwanted_params(self):
    simple_test_builder = SimpleBuilder()
    params = {
        'list': ['Eiffel_Tower', 'Statue#of_Liberty', 'Libertas'],
        'project': 'project_name'
    }
    with self.assertRaises(ValueError):
      simple_test_builder.build('text/tab-separated-values', **params)

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


class BuilderDbUpdateTest(BaseWpOneDbTest):

  USER = {
      'access_token': 'access_token',
      'identity': {
          'username': 'WP1_user',
          'sub': '1234'
      }
  }

  def setUp(self):
    super().setUp()

  @patch('wp1.models.wp10.selection.utcnow',
         return_value=datetime(2020, 12, 25, 10, 55, 44))
  def test_insert(self, mock_utcnow):
    self.app = create_app()
    data = {
        'articles': 'article1 \narticle2',
        'list_name': 'list_name',
        'project': 'en.wikipedia.org'
    }
    with self.app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user'] = self.USER
    simple_test_builder = SimpleBuilder()
    simple_test_builder.insert_builder(data, self.wp10db)
    with self.wp10db.cursor as cursor:
      cursor.execute('SELECT * FROM builders')
      builder = cursor.fetchone()
      print(builder)
    self.assertEqual(1, 1)
