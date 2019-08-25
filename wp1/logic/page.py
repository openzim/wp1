from datetime import datetime
import logging

from wp1.constants import TS_FORMAT, GLOBAL_TIMESTAMP
from wp1.models.wiki.page import Page
from wp1.models.wp10.log import Log
from wp1.models.wp10.move import Move
from wp1.logic import log as logic_log
from wp1.logic import move as logic_move
from wp1.logic.api import page as api_page
import wp1.logic.util as logic_util

logger = logging.getLogger(__name__)


def get_pages_by_category(wikidb, category, ns=None):
  query = '''
      SELECT page_namespace, page_title, page_id, cl_sortkey, cl_timestamp 
      FROM page
      JOIN categorylinks ON page_id = cl_from
      WHERE cl_to = %(category)s
  '''

  params = {'category': category}
  if ns is not None:
    query += ' AND page_namespace = %(ns)s'
    params['ns'] = ns

  with wikidb.cursor() as cursor:
    cursor.execute(query, params)
    while True:
      result = cursor.fetchone()
      if not result:
        break
      yield Page(**result)


def update_page_moved(wp10db, project, old_ns, old_title, new_ns, new_title,
                      move_timestamp_dt):
  logger.debug('Updating moves table for %s -> %s', old_title.decode('utf-8'),
               new_title.decode('utf-8'))
  db_timestamp = move_timestamp_dt.strftime(TS_FORMAT).encode('utf-8')

  existing_move = logic_move.get_move(wp10db, db_timestamp, old_ns, old_title)
  if existing_move is not None:
    logger.debug('Move already recorded: %r', existing_move)
  else:
    new_move = Move(m_timestamp=db_timestamp,
                    m_old_namespace=old_ns,
                    m_old_article=old_title,
                    m_new_namespace=new_ns,
                    m_new_article=new_title)
    logic_move.insert(wp10db, new_move)

  new_log = Log(l_project=project.p_project,
                l_namespace=old_ns,
                l_article=old_title,
                l_action=b'moved',
                l_timestamp=GLOBAL_TIMESTAMP,
                l_old=b'',
                l_new=b'',
                l_revision_timestamp=db_timestamp)
  logic_log.insert_or_update(wp10db, new_log)


def _get_redirects_from_db(wikidb, namespace, title, timestamp_dt):
  wiki_db_title = title.decode('utf-8').replace(' ', '_')
  wikidb.ping()
  args_dict = {'title': wiki_db_title, 'namespace': namespace}
  with wikidb.cursor() as cursor:
    cursor.execute(
        '''
        SELECT rd_namespace, rd_title, page_touched FROM page
        JOIN redirect ON page_id = rd_from AND
             page_title = %(title)s AND page_namespace = %(namespace)s
    ''', args_dict)
    row = cursor.fetchone()
    if row:
      timestamp_dt = datetime.strptime(row['page_touched'].decode('utf-8'),
                                       '%Y%m%d%H%M%S')
      return {
          'dest_ns': row['rd_namespace'],
          'dest_title': row['rd_title'],
          'timestamp_dt': timestamp_dt,
      }
    return None


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
  redir = None
  try:
    redir = api_page.get_redirect(title_with_ns)
  except requests.exceptions.ReadTimeout as e:
    logger.exception('Timeout while reading from API, skipping')

  if redir is not None and redir['timestamp_dt'] > timestamp_dt:
    return {
        'dest_ns': redir['ns'],
        'dest_title': redir['title'].encode('utf-8'),
        'timestamp_dt': redir['timestamp_dt'],
    }
  return None


def get_move_data(wp10db, wikidb, namespace, title, timestamp_dt):
  moves = _get_moves_from_api(wp10db, namespace, title, timestamp_dt)
  if moves:
    return moves

  moves = _get_redirects_from_db(wikidb, namespace, title, timestamp_dt)
  if moves:
    return moves

  moves = _get_redirects_from_api(wp10db, namespace, title, timestamp_dt)
  return moves
