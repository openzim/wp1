from bz2 import BZ2Decompressor

import csv
from datetime import datetime, timedelta
import requests

from wp1.constants import WP1_USER_AGENT
from wp1.exceptions import Wp1ScoreProcessingError
from wp1.wp10_db import connect as wp10_connect


def wiki_languages():
  r = requests.get(
      'https://wikistats.wmcloud.org/api.php?action=dump&table=wikipedias&format=csv',
      headers={'User-Agent': WP1_USER_AGENT})
  try:
    r.raise_for_status()
  except requests.exceptions.HTTPError as e:
    raise Wp1ScoreProcessingError('Could not retrieve wiki list') from e

  reader = csv.reader(r.text.splitlines())
  # Skip the header row
  next(reader, None)
  for row in reader:
    yield row[2]


def raw_pageviews(decode=False):

  def get_pageview_url():
    now = datetime.now()
    dt = datetime(now.year, now.month, 1) - timedelta(weeks=4)
    return dt.strftime(
        'https://dumps.wikimedia.org/other/pageview_complete/monthly/'
        '%Y/%Y-%m/pageviews-%Y%m-automated.bz2')

  def as_bytes():
    url = get_pageview_url()
    with requests.get(url, stream=True,
                      headers={'User-Agent': WP1_USER_AGENT}) as r:
      try:
        r.raise_for_status()
      except requests.exceptions.HTTPError as e:
        raise Wp1ScoreProcessingError('Could not retrieve pageview data') from e

      decompressor = BZ2Decompressor()
      trailing = b''
      # Read data in 32 MB chunks
      for http_chunk in r.iter_content(chunk_size=32 * 1024 * 1024):
        data = decompressor.decompress(http_chunk)
        lines = [line for line in data.split(b'\n') if line]
        if not lines:
          continue

        yield trailing + lines[0]
        yield from lines[1:-1]
        trailing = lines[-1]

  if decode:
    for line in as_bytes():
      yield line.decode('utf-8')
  else:
    yield from as_bytes()


def pageview_components():
  for line in raw_pageviews():
    parts = line.split(b' ')
    if len(parts) != 6 or parts[2] == b'null':
      # Skip pages that don't have a pageid
      continue

    if parts[1] == b'' or parts[1] == b'-':
      # Skip pages that don't have a title
      continue

    # Language code, article name, article page id, views
    yield parts[0].split(b'.')[0], parts[1], parts[2], parts[4]


def update_pageviews(wp10db, lang, article, page_id, views):
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''INSERT INTO page_scores (ps_lang, ps_page_id, ps_article, ps_views)
           VALUES (%(lang)s, %(page_id)s, %(article)s, %(views)s)
           ON DUPLICATE KEY UPDATE ps_views = %(views)s
    ''', {
            'lang': lang,
            'page_id': page_id,
            'article': article,
            'views': views
        })


def update_all_pageviews(filter_lang=None):
  # Convert filter lang to bytes if necessary
  if filter_lang is not None and isinstance(filter_lang, str):
    filter_lang = filter_lang.encode('utf-8')

  wp10db = wp10_connect()
  n = 0
  for lang, article, page_id, views in pageview_components():
    if filter_lang is None or lang == filter_lang:
      update_pageviews(wp10db, lang, article, page_id, views)

    n += 1
    if n >= 10000:
      wp10db.commit()
      n = 0
  wp10db.commit()
