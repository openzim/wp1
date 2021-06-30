import unittest
from wp1.logic import selection


class ValidateArticleNameTest(unittest.TestCase):

  items = '''Eiffel_Tower     \nStatue of Liberty
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
    actual = selection.validate_list(self.items)
    self.assertEqual(expected, actual)
