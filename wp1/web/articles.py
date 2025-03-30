import logging
import urllib.parse

import flask

from wp1.api import get_page, get_revision_id_by_timestamp
from wp1.constants import FRONTEND_WIKI_BASE

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

articles = flask.Blueprint('articles', __name__)


@articles.route('<path:name>/<timestamp>/redirect')
def redirect(name, timestamp): 
  logger.debug(f"Redirect route called with raw name: {name}")
  logger.debug(f"Redirect route called with raw timestamp: {timestamp}")
  # Decode the URL-encoded name
  decoded_name = urllib.parse.unquote(name)
  page = get_page(decoded_name)
  logger.debug(f"Got page: {page}")
  revid = get_revision_id_by_timestamp(page, timestamp)
  logger.debug(f"Got revid: {revid}")
  if revid:
      return flask.redirect(
          '%sindex.php?title=%s&oldid=%s' % (FRONTEND_WIKI_BASE, decoded_name, revid)
      )

  return flask.abort(404)
