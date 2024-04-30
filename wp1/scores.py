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
