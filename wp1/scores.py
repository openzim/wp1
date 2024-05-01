from bz2 import BZ2Decompressor

import csv
import requests

from wp1.exceptions import Wp1ScoreProcessingError
from wp1.wp10_db import connect as wp10_connect


def wiki_languages():
  r = requests.get(
      'https://wikistats.wmcloud.org/api.php?action=dump&table=wikipedias&format=csv'
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


def raw_pageviews(decode=False):

  def as_bytes():
    with requests.get(
        'https://dumps.wikimedia.org/other/pageview_complete/monthly/2024/2024-03/pageviews-202403-automated.bz2',
        stream=True) as r:

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
  wp10db.commit()


def update_all_pageviews():
  wp10db = wp10_connect()
  for lang, article, page_id, views in pageview_components():
    update_pageviews(wp10db, lang, article, page_id, views)
