import http.cookiejar
import logging
import os
import tempfile
from http.cookiejar import MozillaCookieJar

import mwclient
import requests

from wp1.credentials import CREDENTIALS, ENV

logger = logging.getLogger(__name__)
MW_USER_AGENT = "WP1.0Bot/3.0. Run by User:Audiodude. Using mwclient/0.11.0"


def get_credentials():
    try:
        return CREDENTIALS[ENV]["API"]
    except KeyError:
        # No credentials, probably in development environment.
        pass


site = None


def login():
    global site
    if site and site.logged_in:
        logger.debug("Already logged into API site")
        return True

    api_creds = get_credentials()
    if api_creds is None or len(api_creds) == 0:
        logger.warning("Not creating API site object, no credentials")
        return False

    cookie_path = os.path.join(tempfile.gettempdir(), "cookies.txt")
    cookie_jar = MozillaCookieJar(cookie_path)
    if os.path.exists(cookie_path):
        # Load cookies from file, including session cookies (expirydate=0)
        try:
            cookie_jar.load(ignore_discard=True, ignore_expires=True)
        except http.cookiejar.LoadError:
            logger.warning(
                "Cookie jar at %s is corrupted, deleting", cookie_path
            )
            os.remove(cookie_path)
    logger.info("Loaded %d cookies", len(cookie_jar))

    connection = requests.Session()
    connection.cookies = cookie_jar
    connection.headers.update({"User-Agent": MW_USER_AGENT})

    site = mwclient.Site("en.wikipedia.org", pool=connection)
    if not site.logged_in:
        try:
            logger.info("Logging into API site")
            site.login(api_creds["user"], api_creds["pass"])
            logger.info("Saving cookies")
            cookie_jar.save(ignore_discard=True, ignore_expires=True)
        except mwclient.errors.LoginError:
            logger.exception("Exception logging into Wikipedia")
            return False
    return True


def get_page(name):
    if not login():
        logger.error("Could not get page %s because api site is not defined", name)
        return None

    logger.info("Returning API page %s", name)
    return site.pages[name]


def save_page(page, wikicode, msg):
    if not site or not site.logged_in:
        logger.info("Reloading site login")
        if not login():
            logger.warning("Could not save page, no site object")
            return False

        # Get a new copy of the page, since page.save is tied to page.site and
        # that refers to the old site from before we did the re-login. All of this
        # is a workaround for:
        # https://github.com/mwclient/mwclient/issues/231
        page = get_page(page.name)

    logger.info("Saving API page %s", page.name)
    page.save(wikicode, msg)

    return True


def get_revision_id_by_timestamp(page, timestamp):
    try:
        rev = next(page.revisions(start=timestamp, limit=1, prop="ids"))
    except StopIteration:
        return None
    return rev["revid"]
