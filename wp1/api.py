import logging

import mwclient

logger = logging.getLogger(__name__)
_ua = 'WP1.0Bot/3.0. Run by User:Audiodude. Using mwclient/0.9.1'


def get_credentials():
  try:
    from wp1.credentials import ENV, CREDENTIALS
    return CREDENTIALS[ENV]['API']
  except ImportError:
    # No credentials, probably in development environment.
    pass


site = None


def login():
  global site
  try:
    api_creds = get_credentials()
    if api_creds is None:
      logger.warning('Not creating API site object, no credentials')
      return
    site = mwclient.Site('en.wikipedia.org', clients_useragent=_ua)
    site.login(api_creds['user'], api_creds['pass'])
  except mwclient.errors.LoginError:
    logger.exception('Exception logging into wikipedia')


# Global login on startup.
login()


def get_page(name):
  if not site:
    logger.error('Could not get page %s because api site is not defined', name)
    return None

  return site.pages[name]


def save_page(page, wikicode, msg):
  if not site:
    logger.error('Could not save page %s because api site is not defined', page)
    return False

  try:
    page.save(wikicode, msg)
  except mwclient.errors.AssertUserFailedError as e:
    logger.warning('Got login exception, creating new site object')
    login()

    # Get a new copy of the page, since page.save is tied to page.site and
    # that refers to the old site from before we did the re-login. All of this
    # is a workaround for:
    # https://github.com/mwclient/mwclient/issues/231
    page = get_page(page.name)
    page.save(wikicode, msg)
  return True
