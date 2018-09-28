from models.wiki.page import Page
from models.wiki.log import Log
from logic.util import ns_to_int

def get_pages_by_category(wiki_session, category, ns=None):
  q = wiki_session.query(Page).filter(Page.category == category)
  if ns is not None:
    q.filter(Page.namespace == ns)
  yield from q

def get_move_data(wiki_session, wp10_session, namespace, title, timestamp):
  moves = []
  for log in wiki_session.query(Log).filter(
      Log.namespace == namespace).filter(
      Log.title == title).filter(
      Log.type == b'move'):
    dest_ns = None
    dest_title = None
    for prefix, ns_int in ns_to_int(wp10_session).items():
      if log.params.startswith(prefix):
        dest_ns = ns_int
        dest_title = log.params.replace(prefix + b':', '')
        break
    moves.append({
      'dest_ns': dest_ns,
      'dest_title': dest_title,
      'timestamp_dt': log.timestamp_dt
    })

  for move in moves:
    if move['timestamp_dt'] > timestamp:
      return move

  # TODO: Check api for redirect

  return None
