import flask

from wp1.api import get_page, get_revision_id_by_timestamp
from wp1.constants import FRONTEND_WIKI_BASE

articles = flask.Blueprint('articles', __name__)


@articles.route('<name>/<timestamp>/redirect')
def redirect(name, timestamp):
  page = get_page(name)
  revid = get_revision_id_by_timestamp(page, timestamp)

  if revid:
    return flask.redirect('%sindex.php?title=%s&oldid=%s' %
                          (FRONTEND_WIKI_BASE, name, revid))
  else:
    return flask.abort(404)
