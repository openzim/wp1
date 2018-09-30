from models.wiki.page import Page
from models.wiki.log import Log
from logic.api import page as api_page
import logic.util as logic_util

def get_pages_by_category(wiki_session, category, ns=None):
  q = wiki_session.query(Page).filter(Page.category == category)
  if ns is not None:
    q.filter(Page.namespace == ns)
  yield from q

def _get_moves_from_api(wp10title, timestamp):
  title_with_ns = logic_util.title_for_api(wp10_session, namespace, title)
  moves = api_page.get_moves(title_with_ns)
  if moves is not None:
    for move in moves:
      if move['timestamp'] > timestamp:
        return move
  return None

def _get_redirects_from_api(wp10_session, namespace, title, timestamp):
  title_with_ns = logic_util.title_for_api(wp10_session, namespace, title)
  redir = api_page.get_redirect(title_with_ns)
  if redir is not None and redir['timestamp'] > timestamp:
    return {
      'dest_ns': redir['ns'],
      'dest_title': redir['title'].encode('utf-8'),
      'timestamp_dt': redir['timestamp'],
    }
  return None

def get_move_data(wiki_session, wp10_session, namespace, title, timestamp):
  moves = _get_redirects_from_api(namespace, title, timestamp)
  if moves is None:
    moves = _get_moves_from_api(
      wiki_session, wp10_session, namespace, title, timestamp)
  return moves
