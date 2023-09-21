from collections import defaultdict
from datetime import datetime, timedelta
import logging
import re

from wp1 import api
from wp1.conf import get_conf
from wp1.constants import LOG_NS, LOG_DATE_FORMAT, TS_FORMAT, TS_FORMAT_WP10, MAX_LOGS_PER_DAY
from wp1.logic.util import int_to_ns
from wp1.models.wp10.log import Log
from wp1.templates import env as jinja_env
from wp1.time import get_current_datetime
from wp1.wiki_db import connect as wiki_connect
from wp1.wp10_db import connect as wp10_connect

logger = logging.getLogger(__name__)

config = get_conf()
NOT_A_CLASS = config['NOT_A_CLASS'].encode('utf-8')

RE_EXTRACT_TIME = re.compile(r'Log for ([^(]+)')


def log_page_name(project_name):
  return ('Wikipedia:Version_1.0_Editorial_Team/%s_articles_by_quality_log' %
          project_name.decode('utf-8'))


def get_logs(wp10db, project_name, start_dt):
  wp10db.ping()
  with wp10db.cursor() as cursor:
    cursor.execute(
        'SELECT * FROM logging WHERE l_project = %s AND l_timestamp > %s',
        (project_name, start_dt.strftime(TS_FORMAT_WP10)))
    return [Log(**db_log) for db_log in cursor.fetchall()]


def move_target(wp10db, ns, article, db_timestamp):
  wp10db.ping()
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''
      SELECT m_new_namespace as ns, m_new_article as article FROM moves
      WHERE m_old_namespace = %s AND m_old_article = %s AND m_timestamp = %s
    ''', (ns, article, db_timestamp))
    return cursor.fetchone()


def get_revid(wikidb, name, namespace, revision_dt):
  wikidb.ping()
  with wikidb.cursor() as cursor:
    cursor.execute(
        '''
      SELECT rev_id FROM revision JOIN page
         ON page_namespace = %s AND page_title = %s AND rev_page = page_id
      WHERE rev_timestamp <= %s
      ORDER BY rev_timestamp DESC LIMIT 1
    ''', (namespace, name, revision_dt.strftime(TS_FORMAT_WP10)))
    res = cursor.fetchone()
    if res:
      return res['rev_id']


def name_for_article(wp10db, name, namespace):
  format_str = '%s'
  if namespace != 0:
    format_str = ':%s:%%s' % int_to_ns(wp10db)[namespace].decode('utf-8')
  return format_str % name.decode('utf-8').replace('_', ' ')


def talk_page_for_article(wp10db, name, namespace):
  return '%s:%s' % (int_to_ns(wp10db)[namespace + 1].decode('utf-8'),
                    name.decode('utf-8'))


def calculate_logs_to_update(wikidb, wp10db, project_name, from_dt=None):
  """
  Return a dictionary of datetime -> list of log objects that should be
  uploaded to Wikipedia. If from_dt is given, the logs are calculated based on
  those that are newer than that date. Otherwise, the date of the most recently
  uploaded log, as determined by querying the wiki replica, is used.
  """
  from_dt = get_current_datetime() - timedelta(days=7)
  from_dt.replace(hour=23, minute=59, second=59)

  dt_to_log = defaultdict(list)
  for log in get_logs(wp10db, project_name, from_dt):
    dt_to_log[log.timestamp_dt.date()].append(log)
  return dt_to_log


def get_section_categories(logs_for_article):
  renamed = set()
  reassessed = set()
  assessed = set()
  removed = set()
  for article, sublogs in logs_for_article.items():
    if 'moved' in sublogs:
      renamed.add(article)
      continue

    qual = sublogs.get('quality')
    imp = sublogs.get('importance')
    no_old_qual = (not qual or qual.l_old == NOT_A_CLASS)
    no_old_imp = (not imp or imp.l_old == NOT_A_CLASS)
    no_new_qual = (not qual or not qual.l_new or qual.l_new == NOT_A_CLASS)
    no_new_imp = (not imp or not imp.l_new or imp.l_new == NOT_A_CLASS)

    if no_new_qual and no_new_imp:
      removed.add(article)
    elif no_old_qual and no_old_imp:
      assessed.add(article)
    else:
      reassessed.add(article)

  return {
      'renamed': renamed,
      'reassessed': reassessed,
      'assessed': assessed,
      'removed': removed,
  }


def get_section_data(wikidb, wp10db, project_name, dt, logs):
  l = defaultdict(defaultdict)
  for log in logs:
    l[log.l_article][log.l_action.decode('utf-8')] = log

  moved_name = {}
  for article, sublogs in l.items():
    if 'moved' not in sublogs:
      continue
    log = sublogs['moved']
    move = move_target(wp10db, log.l_namespace, log.l_article,
                       log.l_revision_timestamp)
    moved_name[article] = name_for_article(wp10db, move['article'], move['ns'])

  uniq_names = set((log.l_article, log.l_namespace) for log in logs)
  name = dict((n[0], name_for_article(wp10db, n[0], n[1])) for n in uniq_names)
  talk = dict(
      (n[0], talk_page_for_article(wp10db, n[0], n[1])) for n in uniq_names)

  revid = defaultdict(defaultdict)
  talk_revid = defaultdict(defaultdict)
  for log in logs:
    art = log.l_article
    action = log.l_action.decode('utf-8')
    if art in moved_name:
      continue
    revid[art][action] = get_revid(wikidb, log.l_article, log.l_namespace,
                                   log.rev_timestamp_dt)
    talk_revid[art][action] = get_revid(wikidb, log.l_article,
                                        log.l_namespace + 1,
                                        log.rev_timestamp_dt)

  categories = get_section_categories(l)
  # Sort the articles so that the output is idempotent.
  for k, set_ in categories.items():
    categories[k] = sorted(list(set_))

  return {
      **categories,
      'log_date': dt.strftime(LOG_DATE_FORMAT),
      'l': l,
      'name': name,
      'talk': talk,
      'revid': revid,
      'talk_revid': talk_revid,
      'moved_name': moved_name,
  }


def section_for_date(wikidb, wp10db, project_name, dt, logs):
  if len(logs) > MAX_LOGS_PER_DAY:
    return [
        'The log for today is too large to upload. It contains %s entries.' %
        len(logs)
    ]

  template_data = get_section_data(wikidb, wp10db, project_name, dt, logs)
  template = jinja_env.get_template('log_section.jinja2')
  return template.render(template_data)


def generate_log_edits(wikidb, wp10db, project_name, log_map):
  dt_to_sections = {}
  for dt, logs in log_map.items():
    dt_to_sections[dt] = section_for_date(wikidb, wp10db, project_name, dt,
                                          logs)

  dt_sorted = sorted(dt_to_sections.keys(), reverse=True)
  sorted_sections = [dt_to_sections[dt] for dt in dt_sorted]

  # Put in logic to check the length of the sections and break them across
  # multiple pages as appropriate
  return sorted_sections


def update_log_page_for_project(project_name):
  wikidb = wiki_connect()
  wp10db = wp10_connect()
  logging.basicConfig(level=logging.INFO)

  try:
    log_map = calculate_logs_to_update(wikidb, wp10db, project_name)
    edits = generate_log_edits(wikidb, wp10db, project_name, log_map)

    p = api.get_page(log_page_name(project_name))

    header = ('<noinclude>{{Log}}</noinclude>\n')

    if len(edits) == 0:
      today = get_current_datetime()
      from_dt = get_current_datetime() - timedelta(days=7)
      update = ("%s'''There were no logs for this project from %s - %s.'''" %
                (header, from_dt.strftime(LOG_DATE_FORMAT),
                 today.strftime(LOG_DATE_FORMAT)))
    else:
      update = header + '\n'.join(edits)
      i = 1
      while len(update) > 2048 * 1024:
        update = header + '\n'.join(edits[:-1 * i])
        i += 1
        if i == len(edits):
          update = (header + 'Sorry, all of the logs for this date were too '
                    'large to upload.')

    logger.info('Updating logs for %s', project_name)
    api.save_page(p, update, 'Update logs for past 7 days')
  finally:
    if wikidb:
      wikidb.close()
    if wp10db:
      wp10db.close()
