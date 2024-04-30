from bz2 import BZ2Decompressor

import csv
import requests

from wp1.exceptions import Wp1ScoreProcessingError


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


def raw_pageviews(decode=True):

  def as_bytes():
    with requests.get(
        'https://dumps.wikimedia.org/other/pageview_complete/monthly/2024/2024-03/pageviews-202403-automated.bz2',
        stream=True) as r:

      decompressor = BZ2Decompressor()
      trailing = b''
      # Read data in 1 MB chunks
      for http_chunk in r.iter_content(chunk_size=1024 * 1024):
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


def pageviews_for_lang(lang):
  needle = f'{lang}.wikipedia'
  for line in raw_pageviews():
    if needle in line:
      yield line
