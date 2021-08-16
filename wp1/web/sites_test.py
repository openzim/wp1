from datetime import timedelta
from unittest.mock import patch
from wp1.web.app import create_app
from wp1.web.base_web_testcase import BaseWebTestcase


class IdentifyTest(BaseWebTestcase):

  result = {
      'sitematrix': {
          'count':
              2,
          '0': {
              'code': 'aa',
              'name': 'Qaf\u00e1r af',
              'site': [{
                  'url': 'https://aa.wikipedia.org',
                  'dbname': 'aawiki',
                  'code': 'wiki',
                  'sitename': 'Wikipedia',
                  'closed': ''
              },],
              'dir': 'ltr',
              'localname': 'Afar'
          },
          '1': {
              'code': 'ab',
              'name': '\u0410\u04a7\u0441\u0448\u04d9\u0430',
              'site': [{
                  'url':
                      'https://ab.wikipedia.org',
                  'dbname':
                      'abwiki',
                  'code':
                      'wiki',
                  'sitename':
                      '\u0410\u0432\u0438\u043a\u0438\u043f\u0435\u0434\u0438\u0430'
              },],
              'dir': 'ltr',
              'localname': 'Abkhazian'
          },
          'specials': [{
              'url': 'https://advisors.wikimedia.org',
              'dbname': 'advisorswiki',
              'code': 'advisors',
              'lang': 'advisors',
              'sitename': 'Advisors',
              'private': ''
          },]
      },
  }
  sites = ['aa.wikipedia.org', 'ab.wikipedia.org']

  @patch('wp1.web.sites.site')
  def test_get_cached_sites(self, patched_site):
    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      self.redis.setex('sites', timedelta(days=1), value=','.join(self.sites))
      rv = client.get('/v1/sites/')
      self.assertEqual({'sites': self.sites}, rv.get_json())
      self.assertEqual(patched_site.called, False)

  @patch('wp1.web.sites.mwclient.Site')
  def test_get_uncached_sites(self, patched_site):
    patched_site.return_value.api.return_value = self.result
    self.app = create_app()
    with self.override_db(self.app), self.app.test_client() as client:
      rv = client.get('/v1/sites/')
      self.assertEqual({'sites': self.sites}, rv.get_json())
