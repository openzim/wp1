from collections import defaultdict

from jinja2 import Environment, PackageLoader, select_autoescape

from lucky.conf import get_conf
from lucky.constants import LIST_URL
from lucky.wp10_db import connect as wp10_connect

def commas(n):
  return "{:,d}".format(n)

jinja_env = Environment(
    loader=PackageLoader('lucky', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)
jinja_env.filters['commas'] = commas

config = get_conf()
NOT_A_CLASS = config['NOT_A_CLASS'].encode('utf-8')

def get_global_categories():
  assessed = b'Assessed';
  assessed_class = b'Assessed-Class';
  unassessed_class = b'Unassessed-Class';
  unknown_class = b'Unknown-Class';

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
    assessed:        20,
    NOT_A_CLASS:     11, 
    b'Unknown-Class': 10,
    unassessed_class: 0,
  }

  sort_imp= {
    b'Top-Class':    400,
    b'High-Class':   300, 
    b'Mid-Class':    200,
    b'Low-Class':    100, 
    NOT_A_CLASS:     11,
    unknown_class:   10, 
    unassessed_class: 0,
  };
  
  qual_labels = {};
  imp_labels = {};

  for k in sort_qual.keys():
    qual_labels[k] = '{{%s}}' % k.decode('utf-8')

  qual_labels[assessed] = "'''%s'''" % assessed

  for k in sort_imp.keys():
    imp_labels[k] = '{{%s}}' % k.decode('utf-8')

  imp_labels[unassessed_class] = 'No-Class'

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


def generate_global_table_data(stats=None):
  wp10db = wp10_connect()
  try:
    if stats is None:
      stats = get_global_stats(wp10db)
    cat = get_global_categories()

    data = defaultdict(lambda: defaultdict(int))
    cols = {}

    for row in stats:
      # The += here is for 'NotA-Class' classifications, which 
      # could happen either as a result of an actual category or as 
      # the result of the if statements above
      data[row['q']][row['i']] += row['n']
      cols[row['i']] = 1

    # Step 2 - remove any rows or columns that shouldn't be displayed
    to_del = []
    for col in cols.keys():
      if col not in cat['sort_imp']:
        to_del.append(col)
    for c in to_del:
      del cols[c]

    to_del = []
    for r in data.keys():
      if r not in cat['sort_qual']:
        to_del.append(r)
    for r in to_del:
      del data[r]

    ordered_cols = sorted(cols.keys(), key=lambda x: cat['sort_imp'][x],
                          reverse=True)
    ordered_rows = sorted(data.keys(), key=lambda x: cat['sort_qual'][x],
                          reverse=True)

    col_totals = defaultdict(int)
    row_totals = defaultdict(int)
    total = 0
    for col in ordered_cols:
      for row in ordered_rows:
        row_totals[row] += data[row][col]
        col_totals[col] += data[row][col]
        total += data[row][col]

    return {
      'proj': None,
      'create_link': False, # Whether the values link to the web app.
      'data':  data,
      'ordered_cols': ordered_cols,
      'ordered_rows': ordered_rows,
      'row_totals': row_totals,
      'col_totals': col_totals,
      'total': total,
      'col_labels': cat['imp_labels'],
      'row_labels': cat['qual_labels'],
    }
  finally:
    wp10db.close()

def upload_global_table(stats=None):
  table_data = generate_global_table_data(stats=stats)
  wikicode = create_wikicode(table_data)
  print(wikicode)
  

def create_wikicode(table_data):
  template = jinja_env.get_template('table.html.jinja2')
  display = {
    'LIST_URL': LIST_URL,
    'title': 'Test Title Plz Ignore',
    'project': table_data['proj'],
    # Number of columns plus one, plus a column for Total.
    'total_cols': len(table_data['ordered_cols']) + 2,
  }
  return template.render({**table_data, **display})
