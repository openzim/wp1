import logging

import mwclient

logger = logging.getLogger(__name__)
_ua = 'WP1.0Bot/3.0. Run by User:Audiodude. Using mwclient/0.9.1'

site = mwclient.Site('en.wikipedia.org', clients_useragent=_ua)
def login():
  global site
  try:
    from wp1.credentials import API_CREDS
    site.login(API_CREDS['user'], API_CREDS['pass'])
  except LoginError as e:
    logger.exception(e[1]['result'])
  except ImportError:
    # No credentials, probably in development environment.
    pass


# Global login on startup.
login()


def save_page(page, wikicode, msg):
  if not site:
    logger.error('Could not save page %s because api site is not defined', page)
    return

  try:
    page.save(wikicode, msg)
  except mwclient.errors.AssertUserFailedError as e:
    logger.warn('Got login exception, retrying login')
    login()
    page.save(wikicode, msg)
