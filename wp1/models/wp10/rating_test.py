from wp1.base_db_test import BaseWpOneDbTest
from wp1.models.wp10.rating import Rating


class RatingModelTest(BaseWpOneDbTest):

  def setUp(self):
    super().setUp()
    self.rating = Rating(r_project=b'Test Project',
                         r_namespace=4,
                         r_article=b'Test article pages',
                         r_importance=b'NotAClass',
                         r_importance_timestamp=b'2020-04-04T15:55:55Z',
                         r_quality=b'NotAClass',
                         r_quality_timestamp=b'2020-01-13T08:04:20Z')

  def test_to_web_dict_namespace(self):
    expected = {
        'article':
            'Wikipedia:Test article pages',
        'article_link':
            'https://en.wikipedia.org/w/index.php?title=Wikipedia:Test%20article%20pages',
        'article_talk':
            'Wikipedia talk:Test article pages',
        'article_talk_link':
            'https://en.wikipedia.org/w/index.php?title=Wikipedia talk:Test%20article%20pages',
        'article_history_link':
            'https://en.wikipedia.org/w/index.php?title=Wikipedia:Test%20article%20pages&action=history',
        'importance':
            'NotAClass',
        'importance_updated':
            '2020-04-04T15:55:55Z',
        'quality':
            'NotAClass',
        'quality_updated':
            '2020-01-13T08:04:20Z'
    }

    actual = self.rating.to_web_dict(self.wp10db)
    self.assertEqual(expected, actual)

  def test_to_web_dict_no_namespace(self):
    self.rating.r_namespace = 0
    expected = {
        'article':
            'Test article pages',
        'article_link':
            'https://en.wikipedia.org/w/index.php?title=Test%20article%20pages',
        'article_talk':
            'Talk:Test article pages',
        'article_talk_link':
            'https://en.wikipedia.org/w/index.php?title=Talk:Test%20article%20pages',
        'article_history_link':
            'https://en.wikipedia.org/w/index.php?title=Test%20article%20pages&action=history',
        'importance':
            'NotAClass',
        'importance_updated':
            '2020-04-04T15:55:55Z',
        'quality':
            'NotAClass',
        'quality_updated':
            '2020-01-13T08:04:20Z'
    }

    actual = self.rating.to_web_dict(self.wp10db)
    self.assertEqual(expected, actual)
