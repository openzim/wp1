from datetime import datetime
import logging

from lucky.constants import TS_FORMAT, GLOBAL_TIMESTAMP
from lucky.models.wiki.page import Page
from lucky.models.wp10.log import Log
from lucky.models.wp10.move import Move
from lucky.logic.api import page as api_page
import lucky.logic.util as logic_util

logger = logging.getLogger(__name__)

def get_pages_by_category(wiki_session, category, ns=None):
  q = wiki_session.query(Page).filter(Page.category == category)
  if ns is not None:
    q = q.filter(Page.namespace == ns)
  yield from q

def update_page_moved(
    wp10_session, project, old_ns, old_title, new_ns, new_title,
    move_timestamp_dt):
  logger.info('Updating moves table for %s -> %s',
              old_title.decode('utf-8'), new_title.decode('utf-8'))
  db_timestamp = move_timestamp_dt.strftime(TS_FORMAT).encode('utf-8')
  existing_move = wp10_session.query(Move).filter(
    Move.timestamp == db_timestamp).filter(
    Move.old_namespace == old_ns).filter(
    Move.old_article == old_title).first()

  if existing_move is not None:
    logger.warning('Move already recorded: %r', existing_move)
  else:
    new_move = Move(
      timestamp=db_timestamp, old_namespace=old_ns, old_article=old_title,
      new_namespace=new_ns, new_article=new_title)
    wp10_session.add(new_move)

  existing_log = wp10_session.query(Log).filter(
    Log.project == project.project).filter(
    Log.namespace == old_ns).filter(
    Log.article == old_title).filter(
    Log.action == b'moved').filter(
    Log.revision_timestamp == db_timestamp).first()

  if existing_log is not None:
    logger.warning('Move already recorded in logging table: %r', existing_log)
  else:
    new_log = Log(
      project=project.project, namespace=old_ns, article=old_title,
      action=b'moved', timestamp=GLOBAL_TIMESTAMP, old=b'', new=b'',
      revision_timestamp=db_timestamp)
    wp10_session.add(new_log)

def _get_moves_from_api(wp10_session, namespace, title, timestamp_dt):
  title_with_ns = logic_util.title_for_api(wp10_session, namespace, title)
  moves = api_page.get_moves(title_with_ns)
  if moves is not None:
    for move in moves:
      if move['timestamp_dt'] > timestamp_dt:
        return {
          'dest_ns': move['ns'],
          'dest_title': move['title'].encode('utf-8'),
          'timestamp_dt': move['timestamp_dt'],
        }
  return None

def _get_redirects_from_api(wp10_session, namespace, title, timestamp_dt):
  title_with_ns = logic_util.title_for_api(wp10_session, namespace, title)
  redir = api_page.get_redirect(title_with_ns)
  if redir is not None and redir['timestamp_dt'] > timestamp_dt:
    return {
      'dest_ns': redir['ns'],
      'dest_title': redir['title'].encode('utf-8'),
      'timestamp_dt': redir['timestamp_dt'],
    }
  return None

def get_move_data(wp10_session, namespace, title, timestamp_dt):
  moves = _get_redirects_from_api(wp10_session, namespace, title, timestamp_dt)
  if moves is None:
    moves = _get_moves_from_api(wp10_session, namespace, title, timestamp_dt)
  return moves
