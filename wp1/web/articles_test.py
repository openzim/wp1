from unittest.mock import patch

from wp1.web.base_web_testcase import BaseWebTestcase
from wp1.constants import FRONTEND_WIKI_BASE


class ArticlesTest(BaseWebTestcase):

  @patch('wp1.web.articles.get_page')
  @patch('wp1.web.articles.get_revision_id_by_timestamp')
  def test_redirect_response(self, patched_get_revision, patched_get_page):
    patched_get_revision.return_value = 5555

    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get(
          '/v1/articles/Web%20development/2020-01-13T10:00:00Z/redirect')
      self.assertEqual('302 FOUND', rv.status)

      expected_url = ('%sindex.php?title=%s&oldid=%s' %
                      (FRONTEND_WIKI_BASE, 'Web%20development', 5555))
      self.assertEqual(expected_url, rv.headers['Location'])

  @patch('wp1.web.articles.get_page')
  @patch('wp1.web.articles.get_revision_id_by_timestamp')
  def test_404(self, patched_get_revision, patched_get_page):
    patched_get_revision.return_value = None

    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get(
          '/v1/articles/Web%20development/2020-01-13T10:00:00Z/redirect')
      self.assertEqual('404 NOT FOUND', rv.status)
