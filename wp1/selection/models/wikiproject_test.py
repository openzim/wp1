import unittest

from wp1.base_db_test import BaseWpOneDbTest
from wp1.exceptions import Wp1FatalSelectionError
from wp1.selection.models.wikiproject import Builder as WikiProjectBuilder


class WikiProjectTest(BaseWpOneDbTest):

  def setUp(self):
    super().setUp()
    self.builder = WikiProjectBuilder()

    # Four "projects" with a list of somewhat overlapping "articles" for each
    projects = ('Water', 'Fire', 'Wind', 'Èarth')
    water_articles = ('Ocëan', 'Lake')
    fire_articles = ('Campfire', 'Åsh')
    wind_articles = ('Breeze', 'Ocëan', 'Campfire', 'Åsh')
    earth_articles = ('Mountain', 'Cave', 'Åsh')
    all_articles = [
        water_articles, fire_articles, wind_articles, earth_articles
    ]

    all_rows = []
    for i, p in enumerate(projects):
      all_rows.extend(zip((p,) * len(all_articles[i]), all_articles[i]))

    with self.wp10db.cursor() as cursor:
      cursor.executemany(
          'INSERT INTO ratings (r_project, r_namespace, r_article) VALUES (%s, 0, %s)',
          all_rows)
      cursor.executemany(
          'INSERT INTO projects (p_project, p_timestamp) VALUES (%s, 0)',
          projects)

  def test_validate(self):
    params = {
        'add': ['Water', 'Fire', 'Lava'],
        'subtract': ['Wind', 'Èarth', 'Stone']
    }
    actual = self.builder.validate(wp10db=self.wp10db, **params)
    self.assertEqual((['Water', 'Fire', 'Wind', 'Èarth'
                      ], ['Lava', 'Stone'], ['Not all given projects exist']),
                     actual)

  def test_validate_all_valid(self):
    params = {'add': ['Water', 'Fire'], 'subtract': ['Wind', 'Èarth']}
    actual = self.builder.validate(wp10db=self.wp10db, **params)
    self.assertEqual((['Water', 'Fire', 'Wind', 'Èarth'], [], []), actual)

  def test_validate_all_invalid(self):
    params = {'add': ['Lava'], 'subtract': ['Stone']}
    actual = self.builder.validate(wp10db=self.wp10db, **params)
    self.assertEqual(([], ['Lava', 'Stone'], ['Not all given projects exist']),
                     actual)

  def test_validate_missing_add(self):
    params = {'subtract': ['Water', 'Fire']}
    actual = self.builder.validate(wp10db=self.wp10db, **params)
    self.assertEqual(([], [], ['Missing articles to add']), actual)

  def test_validate_missing_subtract(self):
    params = {'add': ['Water', 'Fire']}
    actual = self.builder.validate(wp10db=self.wp10db, **params)
    self.assertEqual((['Water', 'Fire'], [], []), actual)

  def test_build(self):
    params = {'add': ['Water', 'Èarth'], 'subtract': ['Fire']}
    actual = self.builder.build('text/tab-separated-values',
                                wp10db=self.wp10db,
                                **params)

    # Ordering is not stable
    actual_set = set(actual.split(b'\n'))
    expected_set = set((b'Lake', 'Ocëan'.encode('utf-8'), b'Mountain', b'Cave'))

    self.assertEqual(expected_set, actual_set)

  def test_build_single_project(self):
    params = {'add': ['Water']}
    actual = self.builder.build('text/tab-separated-values',
                                wp10db=self.wp10db,
                                **params)

    # Ordering is not stable
    actual_set = set(actual.split(b'\n'))
    expected_set = set((b'Lake', 'Ocëan'.encode('utf-8')))

    self.assertEqual(expected_set, actual_set)

  def test_build_empty_set(self):

    params = {'add': ['Water', 'Èarth'], 'subtract': ['Water', 'Èarth']}
    actual = self.builder.build('text/tab-separated-values',
                                wp10db=self.wp10db,
                                **params)

    self.assertEqual(b'', actual)

  def test_build_multiples(self):
    params = {'add': ['Water', 'Earth', 'Water'], 'subtract': ['Fire', 'Fire']}
    actual = self.builder.build('text/tab-separated-values',
                                wp10db=self.wp10db,
                                **params)

    # Ordering is not stable
    articles = actual.split(b'\n')
    self.assertEqual(2, len(articles))
    actual_set = set(articles)
    expected_set = set((b'Lake', 'Ocëan'.encode('utf-8')))

    self.assertEqual(expected_set, actual_set)

  def test_build_invalid_content_type(self):
    params = {'add': ['Water', 'Èarth'], 'subtract': ['Fire']}
    with self.assertRaises(Wp1FatalSelectionError):
      self.builder.build('foo/bar', wp10db=self.wp10db, **params)

  def test_build_missing_wp10db(self):
    params = {'add': ['Water', 'Èarth'], 'subtract': ['Fire']}
    with self.assertRaises(Wp1FatalSelectionError):
      self.builder.build('text/tab-separated-values', **params)

  def test_build_missing_add(self):
    params = {'subtract': ['Fire']}
    with self.assertRaises(Wp1FatalSelectionError):
      self.builder.build('text/tab-separated-values',
                         wp10db=self.wp10db,
                         **params)
