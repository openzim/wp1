import logging

import mwclient

logger = logging.getLogger(__name__)
_ua = 'WP1.0Bot/3.0. Run by User:Audiodude. Using mwclient/0.9.1'

site = None
def login():
  global site
  try:
    from wp1.credentials import API_CREDS
    site = mwclient.Site('en.wikipedia.org', clients_useragent=_ua)
    site.login(API_CREDS['user'], API_CREDS['pass'])
  except mwclient.errors.LoginError:
    logger.exception('Exception logging into wikipedia')
  except ImportError:
    # No credentials, probably in development environment.
    pass


# Global login on startup.
login()


def save_page(page, wikicode, msg):
  if not site:
    logger.error('Could not save page %s because api site is not defined', page)
    return False

  try:
    page.save(wikicode, msg)
  except mwclient.errors.AssertUserFailedError as e:
    logger.warning('Got login exception, retrying login')
    login()
    page.save(wikicode, msg)
  return True
