from bz2 import BZ2Decompressor
from collections import namedtuple
from contextlib import contextmanager
import logging
import os.path

import csv
from datetime import datetime, timedelta
import requests

from wp1.constants import WP1_USER_AGENT
from wp1.exceptions import Wp1ScoreProcessingError
from wp1.time import get_current_datetime
from wp1.wp10_db import connect as wp10_connect

PageviewRecord = namedtuple('PageviewRecord',
                            ['lang', 'name', 'page_id', 'views'])

logger = logging.getLogger(__name__)

try:
  from wp1.credentials import ENV, CREDENTIALS
except ImportError:
  logger.exception('The file credentials.py must be populated manually in '
                   'order to download pageviews')
  CREDENTIALS = None
  ENV = None


def wiki_languages():
  r = requests.get(
      'https://wikistats.wmcloud.org/api.php?action=dump&table=wikipedias&format=csv',
      headers={'User-Agent': WP1_USER_AGENT},
      timeout=60,
  )
  try:
    r.raise_for_status()
  except requests.exceptions.HTTPError as e:
    raise Wp1ScoreProcessingError('Could not retrieve wiki list') from e

  reader = csv.reader(r.text.splitlines())
  # Skip the header row
  next(reader, None)
  for row in reader:
    yield row[2]


def get_pageview_url(prev=False):
  weeks = 4
  if prev:
    weeks = 8

  now = get_current_datetime()
  dt = datetime(now.year, now.month, 1) - timedelta(weeks=weeks)
  return dt.strftime(
      'https://dumps.wikimedia.org/other/pageview_complete/monthly/'
      '%Y/%Y-%m/pageviews-%Y%m-user.bz2')


def get_pageview_file_path(filename):
  path = CREDENTIALS[ENV]['FILE_PATH']['pageviews']
  os.makedirs(path, exist_ok=True)
  return os.path.join(path, filename)


def get_prev_file_path():
  prev_filename = get_pageview_url(prev=True).split('/')[-1]
  return get_pageview_file_path(prev_filename)


def get_cur_file_path():
  cur_filename = get_pageview_url().split('/')[-1]
  return get_pageview_file_path(cur_filename)


def download_pageviews():
  # Clean up file from last month
  prev_filepath = get_prev_file_path()
  if os.path.exists(prev_filepath):
    os.remove(prev_filepath)

  cur_filepath = get_cur_file_path()
  if os.path.exists(cur_filepath):
    # File already downloaded
    return

  with requests.get(get_pageview_url(), stream=True, timeout=60) as r:
    r.raise_for_status()
    try:
      with open(cur_filepath, 'wb') as f:
        # Read data in 8 MB chunks
        for chunk in r.iter_content(chunk_size=8 * 1024 * 1024):
          f.write(chunk)
    except Exception as e:
      logger.exception('Error downloading pageviews')
      os.remove(cur_filepath)
      raise Wp1ScoreProcessingError('Error downloading pageviews') from e


def raw_pageviews(decode=False):

  def as_bytes():
    decompressor = BZ2Decompressor()
    trailing = b''
    with open(get_cur_file_path(), 'rb') as f:
      while True:
        # Read data in 1 MB chunks
        chunk = f.read(1024 * 1024)
        if not chunk:
          break
        data = decompressor.decompress(chunk)
        lines = [line for line in data.split(b'\n') if line]
        if not lines:
          continue

        # Reunite incomplete lines
        yield trailing + lines[0]
        yield from lines[1:-1]
        trailing = lines[-1]

      # Nothing left, yield the last line
      yield trailing

  if decode:
    for line in as_bytes():
      yield line.decode('utf-8')
  else:
    yield from as_bytes()


def pageview_components():
  tally = None
  for line in raw_pageviews():
    parts = line.split(b' ')
    if len(parts) != 6 or parts[2] == b'null':
      # Skip pages that don't have a pageid
      continue

    if parts[1] == b'' or parts[1] == b'-':
      # Skip pages that don't have a title
      continue

    lang = parts[0].split(b'.')[0]
    name = parts[1]
    page_id = parts[2]
    try:
      views = int(parts[4])
    except ValueError:
      logger.warning('Views field wasn\'t int in pageview dump: %r', line)
      continue

    if (tally is not None and tally.lang == lang and tally.name == name and
        tally.page_id == page_id):
      # This is a view on the same page from a different interface (mobile v
      # desktop etc)
      new_dict = {**tally._asdict(), 'views': tally.views + views}
      tally = PageviewRecord(**new_dict)
    else:
      # Language code, article name, article page id, views
      if tally is not None:
        yield tally.lang, tally.name, tally.page_id, tally.views
      tally = PageviewRecord(lang, name, page_id, views)

  yield tally.lang, tally.name, tally.page_id, tally.views


def reset_missing_articles_pageviews(wp10db):
  with wp10db.cursor() as cursor:
    cursor.execute('''
      UPDATE page_scores
      LEFT JOIN temp_pageviews
      ON page_scores.ps_article = temp_pageviews.tp_article
      SET page_scores.ps_views = 0
      WHERE temp_pageviews.tp_article IS NULL;
      ''')
  wp10db.commit()


def insert_temp_pageviews(wp10db, lang, article, page_id, views):
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''INSERT INTO temp_pageviews (tp_lang, tp_page_id, tp_article, tp_views)
              VALUES (%(lang)s, %(page_id)s, %(article)s, %(views)s)
              ON DUPLICATE KEY UPDATE tp_views = %(views)s
          ''', {
            'lang': lang,
            'page_id': page_id,
            'article': article,
            'views': views
        })


def swap_temp_pageviews_to_scores(wp10db):
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''INSERT INTO page_scores (ps_lang, ps_page_id, ps_article, ps_views)
        SELECT tp_lang, tp_page_id, tp_article, tp_views
        FROM temp_pageviews
        ON DUPLICATE KEY UPDATE ps_views = VALUES(ps_views);''')
    wp10db.commit()


def truncate_temp_pageviews(wp10db):
  with wp10db.cursor() as cursor:
    cursor.execute("TRUNCATE TABLE temp_pageviews;")
  wp10db.commit()


def update_pageviews(filter_lang=None, commit_after=50000):
  download_pageviews()

  # Convert filter lang to bytes if necessary
  if filter_lang is not None and isinstance(filter_lang, str):
    filter_lang = filter_lang.encode('utf-8')

  if filter_lang is None:
    logger.info('Updating all pageviews')
  else:
    logger.info('Updating pageviews for %s', filter_lang.decode('utf-8'))

  wp10db = wp10_connect()
  try:
    truncate_temp_pageviews(wp10db)
    n = 0
    for lang, article, page_id, views in pageview_components():
      if filter_lang is None or lang == filter_lang:
        insert_temp_pageviews(wp10db, lang, article, page_id, views)

      n += 1
      if n >= commit_after:
        logger.debug('Commiting in temp db')
        wp10db.commit()
        n = 0
    wp10db.commit()
    logger.debug('Swaping data from temp db to scores db')
    swap_temp_pageviews_to_scores(wp10db)
    reset_missing_articles_pageviews(wp10db)
    truncate_temp_pageviews(wp10db)
    logger.info('Transaction Done')
  except Exception as e:
    wp10db.rollback()
    truncate_temp_pageviews(wp10db)
    logger.error("Transaction failed: %s", e)


if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO,
                      format='%(levelname)s %(asctime)s: %(message)s')
  update_pageviews()
