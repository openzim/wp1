import logging

import mwclient

from wp1.credentials import CREDENTIALS, ENV
from wp1.environment import Environment

logger = logging.getLogger(__name__)
_ua = 'WP1.0Bot/3.0. Run by User:Audiodude. Using mwclient/0.9.1'


def get_credentials():
  return CREDENTIALS[ENV]['API']


site = None


def login():
  global site
  if ENV == Environment.DEVELOPMENT:
    logger.warning('Not using API, environment=development')
    return
  try:
    api_creds = get_credentials()
    site = mwclient.Site('en.wikipedia.org', clients_useragent=_ua)
    site.login(api_creds.get('user'), api_creds.get('pass'))
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
