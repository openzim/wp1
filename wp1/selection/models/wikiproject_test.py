import unittest

from wp1.base_db_test import BaseWpOneDbTest
from wp1.exceptions import Wp1FatalSelectionError
from wp1.selection.models.wikiproject import Builder as WikiProjectBuilder


class WikiProjectTest(BaseWpOneDbTest):

  def setUp(self):
    super().setUp()
    self.builder = WikiProjectBuilder()

    # Four "projects" with a list of somewhat overlapping "articles" for each
    projects = ('Water_Elements', 'Fire', 'Wind', 'Èarth')
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

      # Add a few category pages that should be excluded from the materialized article lists
      cursor.executemany(
          'INSERT INTO ratings (r_project, r_namespace, r_article) VALUES (%s, 14, %s)',
          [('Water_Elements', 'Famous_bodies_of_water'),
           ('Wind', 'Coastal_breezes')])

  def test_validate(self):
    params = {
        'include': ['Water Elements', 'Fire', 'Lava'],
        'exclude': ['Wind', 'Èarth', 'Stone']
    }
    actual = self.builder.validate(wp10db=self.wp10db, **params)
    self.assertEqual((['Water Elements', 'Fire', 'Wind', 'Èarth'
                      ], ['Lava', 'Stone'], ['Not all given projects exist']),
                     actual)

  def test_validate_all_valid(self):
    params = {
        'include': ['Water Elements', 'Fire'],
        'exclude': ['Wind', 'Èarth']
    }
    actual = self.builder.validate(wp10db=self.wp10db, **params)
    self.assertEqual((['Water Elements', 'Fire', 'Wind', 'Èarth'], [], []),
                     actual)

  def test_validate_all_invalid(self):
    params = {'include': ['Lava'], 'exclude': ['Stone']}
    actual = self.builder.validate(wp10db=self.wp10db, **params)
    self.assertEqual(([], ['Lava', 'Stone'], ['Not all given projects exist']),
                     actual)

  def test_validate_missing_include(self):
    params = {'exclude': ['Water Elements', 'Fire']}
    actual = self.builder.validate(wp10db=self.wp10db, **params)
    self.assertEqual(([], [], ['Missing articles to include']), actual)

  def test_validate_empty_include(self):
    params = {'include': [], 'exclude': ['Water Elements', 'Fire']}
    actual = self.builder.validate(wp10db=self.wp10db, **params)
    self.assertEqual(([], [], ['Missing articles to include']), actual)

  def test_validate_missing_exclude(self):
    params = {'include': ['Water Elements', 'Fire']}
    actual = self.builder.validate(wp10db=self.wp10db, **params)
    self.assertEqual((['Water Elements', 'Fire'], [], []), actual)

  def test_validate_missing_wp10db(self):
    params = {'include': ['Lava'], 'exclude': ['Stone']}
    with self.assertRaises(Wp1FatalSelectionError):
      self.builder.validate(**params)

  def test_build(self):
    params = {'include': ['Water Elements', 'Èarth'], 'exclude': ['Fire']}
    actual = self.builder.build('text/tab-separated-values',
                                wp10db=self.wp10db,
                                **params)

    # Ordering is not stable
    actual_set = set(actual.split(b'\n'))
    expected_set = set((b'Lake', 'Ocëan'.encode('utf-8'), b'Mountain', b'Cave'))

    self.assertEqual(expected_set, actual_set)

  def test_build_single_project(self):
    params = {'include': ['Water Elements']}
    actual = self.builder.build('text/tab-separated-values',
                                wp10db=self.wp10db,
                                **params)

    # Ordering is not stable
    actual_set = set(actual.split(b'\n'))
    expected_set = set((b'Lake', 'Ocëan'.encode('utf-8')))

    self.assertEqual(expected_set, actual_set)

  def test_build_empty_set(self):

    params = {
        'include': ['Water Elements', 'Èarth'],
        'exclude': ['Water Elements', 'Èarth']
    }
    actual = self.builder.build('text/tab-separated-values',
                                wp10db=self.wp10db,
                                **params)

    self.assertEqual(b'', actual)

  def test_build_multiples(self):
    params = {
        'include': ['Water Elements', 'Earth', 'Water Elements'],
        'exclude': ['Fire', 'Fire']
    }
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
    params = {'include': ['Water Elements', 'Èarth'], 'exclude': ['Fire']}
    with self.assertRaises(Wp1FatalSelectionError):
      self.builder.build('foo/bar', wp10db=self.wp10db, **params)

  def test_build_missing_wp10db(self):
    params = {'include': ['Water Elements', 'Èarth'], 'exclude': ['Fire']}
    with self.assertRaises(Wp1FatalSelectionError):
      self.builder.build('text/tab-separated-values', **params)

  def test_build_missing_include(self):
    params = {'exclude': ['Fire']}
    with self.assertRaises(Wp1FatalSelectionError):
      self.builder.build('text/tab-separated-values',
                         wp10db=self.wp10db,
                         **params)

  def test_build_empty_include(self):
    params = {'include': [], 'exclude': ['Fire']}
    with self.assertRaises(Wp1FatalSelectionError):
      self.builder.build('text/tab-separated-values',
                         wp10db=self.wp10db,
                         **params)
