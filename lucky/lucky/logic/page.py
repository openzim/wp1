from datetime import datetime
import logging

from lucky.constants import TS_FORMAT, GLOBAL_TIMESTAMP
from lucky.models.wiki.page import Page
from lucky.models.wp10.log import Log
from lucky.models.wp10.move import Move
from lucky.logic import log as logic_log
from lucky.logic import move as logic_move
from lucky.logic.api import page as api_page
import lucky.logic.util as logic_util

logger = logging.getLogger(__name__)

def get_pages_by_category(wikidb, category, ns=None):
  query = '''
    SELECT page_namespace, page_title, page_id, cl_sortkey, cl_timestamp 
  ''' + '''
    FROM ''' + Page.table_name + '''  /* SLOW_OK */
    JOIN categorylinks ON page_id = cl_from
    WHERE cl_to = %(category)s
  '''

  params = {'category': category}
  if ns is not None:
    query += ' AND page_namespace = %(ns)s'
    params['ns'] = ns
 
  with wikidb.cursor() as cursor:
    cursor.execute(query, params)
    return [Page(**db_page) for db_page in cursor.fetchall()]


def update_page_moved(
    wp10db, project, old_ns, old_title, new_ns, new_title,
    move_timestamp_dt):
  logger.info('Updating moves table for %s -> %s',
              old_title.decode('utf-8'), new_title.decode('utf-8'))
  db_timestamp = move_timestamp_dt.strftime(TS_FORMAT).encode('utf-8')
  logging.warning('db_timestamp: %r', db_timestamp)

  existing_move = logic_move.get_move(wp10db, db_timestamp, old_ns, old_title)
  if existing_move is not None:
    logger.warning('Move already recorded: %r', existing_move)
  else:
    new_move = Move(
      m_timestamp=db_timestamp, m_old_namespace=old_ns, m_old_article=old_title,
      m_new_namespace=new_ns, m_new_article=new_title)
    logic_move.insert(wp10db, new_move)

  new_log = Log(
    l_project=project.p_project, l_namespace=old_ns, l_article=old_title,
    l_action=b'moved', l_timestamp=GLOBAL_TIMESTAMP, l_old=b'', l_new=b'',
    l_revision_timestamp=db_timestamp)
  logic_log.insert_or_update(wp10db, new_log)


def _get_moves_from_api(wp10db, namespace, title, timestamp_dt):
  title_with_ns = logic_util.title_for_api(wp10db, namespace, title)
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


def _get_redirects_from_api(wp10db, namespace, title, timestamp_dt):
  title_with_ns = logic_util.title_for_api(wp10db, namespace, title)
  redir = api_page.get_redirect(title_with_ns)
  if redir is not None and redir['timestamp_dt'] > timestamp_dt:
    return {
      'dest_ns': redir['ns'],
      'dest_title': redir['title'].encode('utf-8'),
      'timestamp_dt': redir['timestamp_dt'],
    }
  return None


def get_move_data(wp10db, namespace, title, timestamp_dt):
  moves = _get_redirects_from_api(wp10db, namespace, title, timestamp_dt)
  if moves is None:
    moves = _get_moves_from_api(wp10db, namespace, title, timestamp_dt)
  return moves
