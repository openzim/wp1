from collections import defaultdict
import logging

from wp1 import api
from wp1.conf import get_conf
from wp1.constants import LIST_URL
from wp1.models.wp10.category import Category
from wp1.models.wp10.rating import Rating
from wp1.templates import env as jinja_env
from wp1.wp10_db import connect as wp10_connect

logger = logging.getLogger(__name__)

config = get_conf()
NOT_A_CLASS = config['NOT_A_CLASS'].encode('utf-8')
ASSESSED_CLASS = b'Assessed-Class'
UNASSESSED_CLASS = b'Unassessed-Class'

def labels_for_classes(sort_qual, sort_imp):
  qual_labels = {}
  imp_labels = {}

  for k in sort_qual.keys():
    qual_labels[k] = '{{%s}}' % k.decode('utf-8')
  qual_labels[ASSESSED_CLASS] = "{{Assessed-Class}}"
  qual_labels[UNASSESSED_CLASS] = "'''Unassessed'''"

  for k in sort_imp.keys():
    imp_labels[k] = '{{%s}}' % k.decode('utf-8')
  imp_labels[UNASSESSED_CLASS] = 'No-Class'

  return qual_labels, imp_labels


def get_global_categories():
  sort_qual = {
    b'FA-Class':     500,
    b'FL-Class':     480,
    b'A-Class':      425, 
    b'GA-Class':     400,
    b'B-Class':      300,
    b'C-Class':      225, 
    b'Start-Class':  150,
    b'Stub-Class':   100,
    b'List-Class':    80, 
    ASSESSED_CLASS:   20,
    NOT_A_CLASS:      11,
    b'Unknown-Class': 10,
    UNASSESSED_CLASS:  0,
  }

  sort_imp= {
    b'Top-Class':    400,
    b'High-Class':   300, 
    b'Mid-Class':    200,
    b'Low-Class':    100, 
    NOT_A_CLASS:      11,
    b'Unknown-Class': 10,
    UNASSESSED_CLASS:  0,
  }
  
  qual_labels, imp_labels = labels_for_classes(sort_qual, sort_imp)

  return {
    'sort_qual': sort_qual,
    'sort_imp': sort_imp,
    'qual_labels': qual_labels,
    'imp_labels': imp_labels,
  }


def get_global_stats(wp10db):
  with wp10db.cursor() as cursor:
    cursor.execute('''
      SELECT count(distinct a_article) as n,
             grq.gr_rating as q, gri.gr_rating as i
      FROM global_articles
        JOIN global_rankings as grq
          ON grq.gr_type = 'quality' AND grq.gr_ranking = a_quality
        JOIN global_rankings as gri 
          ON gri.gr_type = 'importance' AND gri.gr_ranking = a_importance
      GROUP BY grq.gr_rating, gri.gr_rating
    ''')
    return cursor.fetchall()


def get_project_stats(wp10db, project_name):
  with wp10db.cursor() as cursor:
    cursor.execute('''
      SELECT count(r_article) as n, r_quality as q, r_importance as i,
             r_project as project
      FROM ''' + Rating.table_name + '''
      WHERE r_project = %s group by r_quality, r_importance, r_project
    ''', (project_name,))
    return cursor.fetchall()


def db_project_categories(wp10db, project_name):
  with wp10db.cursor() as cursor:
    cursor.execute('SELECT c_type, c_rating, c_ranking, c_category FROM ' +
                   Category.table_name + ' WHERE c_project = %s', (project_name,))

    return cursor.fetchall()


def get_project_categories(wp10db, project_name):
  sort_imp = {}
  sort_qual = {}

  categories = db_project_categories(wp10db, project_name)

  for row in categories:
    if row['c_type'] == b'quality':
      sort_qual[row['c_rating']] = row['c_ranking']
    elif row['c_type'] == b'importance':
      sort_imp[row['c_rating']] = row['c_ranking']

  qual_labels, imp_labels = labels_for_classes(sort_qual, sort_imp)

  for row in categories:
    if row['c_rating'] == NOT_A_CLASS:
      if row['c_type'] == b'quality':
        qual_labels[row['c_rating']] = (' style="text-align: center;" '
                                        "| '''Other'''")
      elif row['c_type'] == b'importance':
        imp_labels[row['c_rating']] = 'Other'
    else:
      if row['c_type'] == b'quality':
        labels = qual_labels
      elif row['c_type'] == b'importance':
        labels = imp_labels
        
      labels[row['c_rating']] = (
        '{{%s|category=Category:%s}}' % (row['c_rating'].decode('utf-8'),
                                         row['c_category'].decode('utf-8'))
      )
                       
  return {
    'sort_qual': sort_qual,
    'sort_imp': sort_imp,
    'qual_labels': qual_labels,
    'imp_labels': imp_labels,
  }


def data_for_stats(stats):
  data = defaultdict(lambda: defaultdict(int))
  cols = {}

  for row in stats:
    # The += here is for 'NotA-Class' classifications, which
    # could happen either as a result of an actual category or as
    # the result of the if statements above
    data[row['q']][row['i']] += row['n']
    cols[row['i']] = 1

  return data, cols


def generate_table_data(stats, categories, table_overrides=None):
  if table_overrides is None:
    table_overrides = {}

  # Step 1 - populate the basic data dictionaries.
  data, cols = data_for_stats(stats)

  # Step 2 - remove any rows or columns that shouldn't be displayed
  to_del = []
  for col in cols.keys():
    if col not in categories['sort_imp']:
      to_del.append(col)
  for c in to_del:
    del cols[c]

  to_del = []
  for r in data.keys():
    if r not in categories['sort_qual']:
      print(r)
      to_del.append(r)
  for r in to_del:
    del data[r]

  # Step 3 - Sort the rows and columns by their ranking value
  ordered_cols = sorted(cols.keys(), key=lambda x: categories['sort_imp'][x],
                        reverse=True)
  ordered_rows = sorted(data.keys(), key=lambda x: categories['sort_qual'][x],
                        reverse=True)
  if UNASSESSED_CLASS in ordered_rows:
    idx = ordered_rows.index(UNASSESSED_CLASS)
    ordered_rows = (ordered_rows[:idx] + [b'Assessed-Class'] +
                    ordered_rows[idx:])
  else:
    ordered_rows.append(b'Assessed-Class')

  # Step 4 - Get the totals for each row and column
  col_totals = defaultdict(int)
  row_totals = defaultdict(int)
  total = 0
  for col in ordered_cols:
    for row in ordered_rows:
      d = data[row].get(col, 0)
      row_totals[row] += d
      col_totals[col] += d
      total += d

  # Step 5 - Get the 'assessed' total, which is just total - unassessed
  for col in ordered_cols:
    d = col_totals[col] - data[b'Unassessed-Class'].get(col, 0)
    data[b'Assessed-Class'][col] = d
    row_totals[b'Assessed-Class'] += d

  ans = {
    **table_overrides,
    'data':  data,
    'ordered_cols': ordered_cols,
    'ordered_rows': ordered_rows,
    'row_totals': row_totals,
    'col_totals': col_totals,
    'total': total,
    'col_labels': categories['imp_labels'],
    'row_labels': categories['qual_labels'],
  }

  # If we have only one column, don't display it because it is identical to the
  # total anyways.
  if len(ordered_cols) < 2:
    ans['is_single_col'] = True
    ans['ordered_cols'] = []
    ans['title'] = '%s pages by quality' % ans['project_display']

  return ans


def generate_project_table_data(wp10db, project_name):
    stats = get_project_stats(wp10db, project_name)
    categories = get_project_categories(wp10db, project_name)
    project_display = project_name.decode('utf-8').replace('_', ' ')
    title = ('%s articles by quality and importance' % project_display)

    return generate_table_data(stats, categories, {
      'project': project_name,
      'project_display': project_display,
      'create_link': True,
      'title': title,
      'center_table': False,
    })


def generate_global_table_data(wp10db):
  stats = get_global_stats(wp10db)
  categories = get_global_categories()

  return generate_table_data(stats, categories, {
    'project': None,
    'project_display': 'All articles',
    'create_link': False, # Whether the values link to the web app.
    'title': 'All rated articles by quality and importance',
    'center_table': True,
  })


def upload_project_table(project_name):
  logging.basicConfig(level=logging.DEBUG)
  wp10db = wp10_connect()

  try:
    logger.info('Getting table data for project: %s',
                project_name.decode('utf-8'))
    table_data = generate_project_table_data(wp10db, project_name)
    wikicode = create_wikicode(table_data)
    page_name = ('User:WP 1.0 bot/Tables/Project/%s' %
                 project_name.decode('utf-8'))
    page = api.get_page(page_name)
    logger.info('Uploading wikicode to Wikipedia: %s',
                project_name.decode('utf-8'))
    api.save_page(page, wikicode, 'Copying assessment table to wiki.')
  finally:
    if wp10db is not None:
      wp10db.close()


def upload_global_table():
  logging.basicConfig(level=logging.DEBUG)
  wp10db = wp10_connect()

  try:
    logger.info('Getting table data for: global table')
    table_data = generate_global_table_data(wp10db)
    wikicode = create_wikicode(table_data)
    page_name = 'User:WP 1.0 bot/Tables/OverallArticles'
    logger.info('Uploading wikicode to Wikipedia: global table')
    page = api.get_page(page_name)
    api.save_page(page, wikicode, 'Copying assessment table to wiki.')
  finally:
    if wp10db is not None:
      wp10db.close()

def create_wikicode(table_data):
  template = jinja_env.get_template('table.jinja2')
  display = {
    'LIST_URL': LIST_URL,
    # Number of columns plus one, plus a column for Total.
    'total_cols': len(table_data['ordered_cols']) + 2,
  }
  return template.render({**table_data, **display})
