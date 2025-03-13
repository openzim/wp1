from unittest.mock import MagicMock, patch

from wp1.base_db_test import BaseWpOneDbTest, get_first_selection
from wp1.exceptions import Wp1FatalSelectionError
from wp1.models.wp10.builder import Builder
from wp1.selection.models.book import Builder as BookBuilder

import requests


class BookBuilderTest(BaseWpOneDbTest):
  mock_book_response = {
      'batchcomplete': "",
      'query': {
          'pages': {
              74370036: {
                  'pageid':
                      74370036,
                  'ns':
                      2,
                  'title':
                      "User:Audiodude/Books/test",
                  'revisions': [{
                      'slots': {
                          'main': {
                              'contentmodel':
                                  "wikitext",
                              'contentformat':
                                  "text/x-wiki",
                              '*':
                                  """{{saved book
 |title=
 |subtitle=
 |cover-image=
 |cover-color=}}

:[[Katrina Kaif]]
:[[Hindi]]
:[[Kaizad Gustad]]
:[[List of awards and nominations received by Katrina Kaif]]
:[[Screen Awards]]
:[[Zee Cine Awards]]
:[[Filmfare Awards]]
:[[Katrina Kaif]]
:[[Hindi]]
:[[Kaizad Gustad]]
:[[List of awards and nominations received by Katrina Kaif]]
:[[Screen Awards]]
:[[Zee Cine Awards]]
:[[Filmfare Awards]]
:[[John Smith (explorer)]]"""
                          }
                      }
                  }]
              }
          }
      }
  }

  def setUp(self):
    super().setUp()
    self.s3 = MagicMock()
    self.builder_model = Builder(
        b_id=b'1a-2b-3c-4d',
        b_name=b'Book Builder',
        b_user_id=1234,
        b_project=b'en.wikipedia.fake',
        b_model=b'wp1.selection.models.book',
        b_params=
        '{"url":"https://en.wikipedia.fake/wiki/User:Audiodude/Books/test"}')
    self.builder = BookBuilder()

  @patch('wp1.selection.models.book.requests')
  def test_materialize(self, mock_requests):
    mock_response = MagicMock()
    mock_response.json.return_value = self.mock_book_response
    mock_requests.get.return_value = mock_response

    self.builder.materialize(self.s3, self.wp10db, self.builder_model,
                             'text/tab-separated-values', 1)
    actual = get_first_selection(self.wp10db)
    self.assertEqual(actual.s_content_type, b'text/tab-separated-values')
    self.assertEqual(actual.s_builder_id, b'1a-2b-3c-4d')

  @patch('wp1.selection.models.book.requests')
  def test_build(self, mock_requests):
    mock_response = MagicMock()
    mock_response.json.return_value = self.mock_book_response
    mock_requests.get.return_value = mock_response

    actual = self.builder.build(
        'text/tab-separated-values',
        url='https://en.wikipedia.fake/wiki/User:Audiodude/Books/test',
        project='en.wikipedia.fake')
    self.assertEqual(
        b'Katrina_Kaif\nHindi\nKaizad_Gustad\n'
        b'List_of_awards_and_nominations_received_by_Katrina_Kaif\nScreen_Awards\n'
        b'Zee_Cine_Awards\nFilmfare_Awards\nJohn_Smith_(explorer)', actual)

  def test_build_wrong_content_type(self):
    with self.assertRaises(Wp1FatalSelectionError):
      actual = self.builder.build(
          None,
          url='https://en.wikipedia.fake/wiki/User:Audiodude/Books/test',
          project='en.wikipedia.fake')

  def test_build_missing_url(self):
    with self.assertRaises(Wp1FatalSelectionError):
      actual = self.builder.build('text/tab-separated-values')

  def test_build_url_not_str(self):
    with self.assertRaises(Wp1FatalSelectionError):
      actual = self.builder.build(
          'text/tab-separated-values',
          url=['https://en.wikipedia.fake/wiki/User:Audiodude/Books/test'],
          project='en.wikipedia.fake')

  @patch('wp1.selection.models.book.requests')
  def test_build_proper_api_call(self, mock_requests):
    mock_response = MagicMock()
    mock_response.json.return_value = self.mock_book_response
    mock_requests.get.return_value = mock_response

    actual = self.builder.build(
        'text/tab-separated-values',
        url='https://en.wikipedia.fake/wiki/User:Audiodude/Books/test',
        project='en.wikipedia.fake')
    mock_requests.get.assert_called_with(
        'https://en.wikipedia.fake/w/api.php?'
        'action=query&prop=revisions&rvprop=content&format=json&rvslots=main'
        '&titles=User:Audiodude/Books/test',
        headers={
            'User-Agent': 'WP 1.0 bot 1.0.0/Audiodude <audiodude@gmail.com>'
        })

  @patch('wp1.selection.models.book.requests.get')
  def test_build_non_200(self, mock_requests_get):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
    mock_requests_get.return_value = mock_response

    with self.assertRaises(Wp1FatalSelectionError):
      actual = self.builder.build(
          'text/tab-separated-values',
          url='https://en.wikipedia.fake/wiki/User:Audiodude/Books/test',
          project='en.wikipedia.fake')

  def test_validate_missing_url(self):
    actual = self.builder.validate('text/tab-separated-values',
                                   project='en.wikipedia.fake')
    self.assertEquals(('', '', ['Missing URL parameter']), actual)

  def test_validate_missing_url(self):
    actual = self.builder.validate(
        url='https://en.wikipedia.fake/wiki/User:Audiodude/Books/test',)
    self.assertEqual(
        ('', 'https://en.wikipedia.fake/wiki/User:Audiodude/Books/test',
         ['Missing project parameter']), actual)

  def test_validate_project_mismatch(self):
    actual = self.builder.validate(
        url='https://fr.wikipedia.fake/wiki/User:Audiodude/Books/test',
        project='en.wikipedia.fake')
    self.assertEqual(
        ('', 'https://fr.wikipedia.fake/wiki/User:Audiodude/Books/test', [
            'The domain of your URL does not match your '
            'selected project (project is: en.wikipedia.fake, URL has: fr.wikipedia.fake)'
        ]), actual)
