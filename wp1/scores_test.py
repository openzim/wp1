import bz2
from datetime import datetime
import os.path
import unittest
from unittest.mock import patch, MagicMock, mock_open

import requests

from wp1.base_db_test import BaseWpOneDbTest
from wp1.constants import WP1_USER_AGENT
from wp1.exceptions import Wp1ScoreProcessingError
from wp1 import scores

pageview_text = b'''af.wikipedia 1701 1402 desktop 4 F1
af.wikipedia 1701 1402 mobile-web 3 O2T1
af.wikipedia 1702 1404 mobile-web 3 L1O2
af.wikipedia 1702 1404 desktop 1 P1
af.wikipedia 1703 1405 mobile-web 3 C1O2
af.wikipedia 1703 1405 desktop 1 ^1
af.wikipedia 1704 1406 mobile-web 4 A1O2T1
af.wikipedia 1704 1406 desktop 2 F1
af.wikipedia 1705 1407 mobile-web 3 O3
af.wikipedia 1705 1407 desktop 1 F1
af.wikipedia 1706 1408 desktop 8 H8
af.wikipedia 1706 1408 mobile-web 4 C1O2Y1
af.wikipedia 1707 1409 mobile-web 2 O2
af.wikipedia 1707 1409 desktop 3 H1J1
af.wikipedia 1708 1410 desktop 4 V1]1
af.wikipedia 1708 1410 mobile-web 1 O1
af.wikipedia 1709 1411 desktop 2 F1
af.wikipedia 1709 1411 mobile-web 2 O2
af.wikipedia \xc3\xa9\xc3\xa1\xc3\xb8 3774 mobile-web 1 A1
af.wikipedia \xc3\xa9\xc3\xa1\xc3\xb8 3774 mobile-web 2 F2
af.wikipedia 1711 752 mobile-web 4 C1O2U1
af.wikipedia 1711 752 desktop 1 K1
af.wikipedia 1712 753 mobile-web 2 O2
af.wikipedia 1712 753 desktop 20 E12J7U1'''

pageview_error_text = b'''af.wikipedia 1701 1402 desktop 4 F1
af.wikipedia 1701 1402 mobile-web 3 O2T1
af.wikipedia 1702 1404 mobile-web 3 L1O2
af.wikipedia 1702 1404 desktop 1 P1
af.wikipedia - 1405 mobile-web 3 C1O2
af.wikipedia - 1405 desktop 1 ^1
af.wikipedia 1704 1406 mobile-web 4 A1O2T1
af.wikipedia 1704 1406 desktop 2 F1
af.wikipedia 1705 1407 mobile-web 3 O3
af.wikipedia 1705 1407 desktop 1 F1
af.wikipedia 1706 desktop 8 H8
af.wikipedia 1706 mobile-web 4 C1O2Y1
af.wikipedia 1707 1409 mobile-web 2 O2
af.wikipedia 1707 1409 desktop 3 H1J1
af.wikipedia 1708 1410 desktop X V1]1
af.wikipedia 1708 1410 mobile-web Z O1
af.wikipedia 1709 1411 desktop 2 F1
af.wikipedia 1709 1411 mobile-web 2 O2
af.wikipedia \xc3\xa9\xc3\xa1\xc3\xb8 3774 mobile-web 1 A1
af.wikipedia \xc3\xa9\xc3\xa1\xc3\xb8 3774 mobile-web 2 F2
af.wikipedia 1711 752 mobile-web 4 C1O2U1
af.wikipedia 1711 752 desktop 1 K1
af.wikipedia 1712 753 mobile-web 2 O2
af.wikipedia 1712 753 desktop 20 E12J7U1'''

pageview_bz2 = bz2.compress(pageview_text)
pageview_error_bz2 = bz2.compress(pageview_error_text)


class ScoresTest(BaseWpOneDbTest):

  @patch('wp1.scores.requests')
  def test_wiki_languages(self, mock_requests):
    mock_response = MagicMock()
    mock_response.text = (
        'id,lang,prefix,total,good,views,edits,users,admins,ts,loclang,images,'
        'loclanglink,activeusers,version,si_mainpage,si_base,si_sitename,si_generator,'
        'si_phpversion,si_phpsapi,si_dbtype,si_dbversion,si_rev,si_case,si_rights,'
        'si_lang,si_fallback8bitEncoding,si_writeapi,si_timezone,si_timeoffset,'
        'si_articlepath,si_scriptpath,si_script,si_variantarticlepath,si_server,'
        'si_wikiid,si_time,method,http,status,ratio\n'
        '2,English,en,60556624,6818615,63208806,1216695232,47328206,861,"2024-04-30 00:06:16",'
        'English,916605,English_language,122676,1.28.0-wmf.13,,,,"MediaWiki 1.43.0-wmf.2",,,,,'
        ',,,,,,,,,,,,,,,8,200,a,0.1126\n'
        '153,Cebuano,ceb,11228672,6118766,0,35037562,115188,5,"2024-04-30 00:01:34"'
        ',"Sinugboanong Binisaya",1,Sinugboanon,149,1.28.0-wmf.13,,,,"MediaWiki 1.43.0-wmf.2",,'
        ',,,,,,,,,,,,,,,,,,8,200,a,0.5449\n'
        '10,German,de,8007675,2905495,8543798,242922549,4359000,174,"2024-04-30 00:08:06",'
        'Deutsch,129233,Deutsch,17684,1.28.0-wmf.13,,,,"MediaWiki 1.43.0-wmf.2",,,,,,,,,,,,,,,,,'
        ',,,8,200,a,0.3628\n'
        '1,French,fr,13037937,2608568,2234272,214217598,4914029,146,"2024-04-30 00:08:24",'
        'Fran&#231;ais,71651,Fran&#231;ais,16929,1.28.0-wmf.13,,,,"MediaWiki 1.43.0-wmf.2",,,,,,,'
        ',,,,,,,,,,,,,8,200,a,0.2001\n')
    mock_requests.get.return_value = mock_response

    actual = list(scores.wiki_languages())
    self.assertEqual(['en', 'ceb', 'de', 'fr'], actual)

  @patch('wp1.scores.requests')
  def test_wiki_languages_raises_on_http_error(self, mock_requests):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
    mock_requests.exceptions.HTTPError = requests.exceptions.HTTPError
    mock_requests.get.return_value = mock_response

    with self.assertRaises(Wp1ScoreProcessingError):
      list(scores.wiki_languages())

  @patch('wp1.scores.get_current_datetime', return_value=datetime(2024, 5, 25))
  def test_get_pageview_url(self, mock_datetime):
    actual = scores.get_pageview_url()
    self.assertEqual(
        'https://dumps.wikimedia.org/other/pageview_complete/monthly/'
        '2024/2024-04/pageviews-202404-user.bz2', actual)

  @patch('wp1.scores.get_current_datetime', return_value=datetime(2024, 5, 25))
  def test_get_pageview_url_prev(self, mock_datetime):
    actual = scores.get_pageview_url(prev=True)
    self.assertEqual(
        'https://dumps.wikimedia.org/other/pageview_complete/monthly/'
        '2024/2024-03/pageviews-202403-user.bz2', actual)

  @patch('wp1.scores.get_current_datetime', return_value=datetime(2024, 5, 25))
  def test_get_prev_file_path(self, mock_datetime):
    actual = scores.get_prev_file_path()
    self.assertEqual('/tmp/pageviews/pageviews-202403-user.bz2', actual)

  @patch('wp1.scores.get_current_datetime', return_value=datetime(2024, 5, 25))
  def test_get_cur_file_path(self, mock_datetime):
    actual = scores.get_cur_file_path()
    self.assertEqual('/tmp/pageviews/pageviews-202404-user.bz2', actual)

  def test_get_pageview_file_path(self):
    actual = scores.get_pageview_file_path('pageviews-202404-user.bz2')
    self.assertEqual('/tmp/pageviews/pageviews-202404-user.bz2', actual)

  @patch('wp1.scores.get_current_datetime', return_value=datetime(2024, 5, 25))
  @patch('wp1.scores.requests.get')
  def test_download_pageviews(self, mock_get_response, mock_datetime):
    context = MagicMock()
    resp = MagicMock()
    resp.iter_content.return_value = (pageview_bz2,)
    context.__enter__.return_value = resp
    mock_get_response.return_value = context

    file_path = scores.get_cur_file_path()
    if os.path.exists(file_path):
      os.remove(file_path)

    scores.download_pageviews()

    mock_get_response.assert_called_once()
    self.assertTrue(os.path.exists(file_path))

  @patch('wp1.scores.get_current_datetime', return_value=datetime(2024, 5, 25))
  @patch('wp1.scores.requests.get')
  def test_download_pageviews_remove_prev(self, mock_get_response,
                                          mock_datetime):
    context = MagicMock()
    resp = MagicMock()
    resp.iter_content.return_value = (pageview_bz2,)
    context.__enter__.return_value = resp
    mock_get_response.return_value = context

    file_path = scores.get_prev_file_path()
    # Create empty file
    open(file_path, 'a').close()

    scores.download_pageviews()

    self.assertFalse(os.path.exists(file_path))

  @patch('wp1.scores.get_current_datetime', return_value=datetime(2024, 5, 25))
  @patch('wp1.scores.requests.get')
  def test_download_pageviews_skip_existing(self, mock_get_response,
                                            mock_datetime):
    context = MagicMock()
    resp = MagicMock()
    resp.iter_content.return_value = (pageview_bz2,)
    context.__enter__.return_value = resp
    mock_get_response.return_value = context

    file_path = scores.get_cur_file_path()
    # Create empty file
    open(file_path, 'a').close()

    scores.download_pageviews()

    mock_get_response.assert_not_called()
    self.assertTrue(os.path.exists(file_path))

  @patch('wp1.scores.get_current_datetime', return_value=datetime(2024, 5, 25))
  @patch("builtins.open", new_callable=mock_open, read_data=pageview_bz2)
  def test_raw_pageviews(self, mock_file_open, mock_datetime):
    actual = b'\n'.join(scores.raw_pageviews())

    self.assertEqual(pageview_text, actual)

  @patch('wp1.scores.get_current_datetime', return_value=datetime(2024, 5, 25))
  @patch("builtins.open", new_callable=mock_open, read_data=pageview_bz2)
  def test_raw_pageviews_decode(self, mock_file_open, mock_datetime):
    actual = '\n'.join(scores.raw_pageviews(decode=True))

    self.assertEqual(pageview_text.decode('utf-8'), actual)

  @patch("builtins.open", new_callable=mock_open, read_data=pageview_bz2)
  def test_pageview_components(self, mock_file_open):
    expected = [
        (b'af', b'1701', b'1402', 7),
        (b'af', b'1702', b'1404', 4),
        (b'af', b'1703', b'1405', 4),
        (b'af', b'1704', b'1406', 6),
        (b'af', b'1705', b'1407', 4),
        (b'af', b'1706', b'1408', 12),
        (b'af', b'1707', b'1409', 5),
        (b'af', b'1708', b'1410', 5),
        (b'af', b'1709', b'1411', 4),
        (b'af', b'\xc3\xa9\xc3\xa1\xc3\xb8', b'3774', 3),
        (b'af', b'1711', b'752', 5),
        (b'af', b'1712', b'753', 22),
    ]

    actual = list(scores.pageview_components())

    self.assertEqual(expected, actual)

  @patch("builtins.open", new_callable=mock_open, read_data=pageview_error_bz2)
  def test_pageview_components_errors(self, mock_file_open):
    expected = [
        (b'af', b'1701', b'1402', 7),
        (b'af', b'1702', b'1404', 4),
        (b'af', b'1704', b'1406', 6),
        (b'af', b'1705', b'1407', 4),
        (b'af', b'1707', b'1409', 5),
        (b'af', b'1709', b'1411', 4),
        (b'af', b'\xc3\xa9\xc3\xa1\xc3\xb8', b'3774', 3),
        (b'af', b'1711', b'752', 5),
        (b'af', b'1712', b'753', 22),
    ]

    actual = list(scores.pageview_components())

    self.assertEqual(expected, actual)

  def test_update_db_pageviews(self):
    scores.update_db_pageviews(self.wp10db, 'en', 'Statue_of_Liberty', 1234,
                               100)

    with self.wp10db.cursor() as cursor:
      cursor.execute('SELECT * FROM page_scores WHERE ps_page_id = 1234')
      result = cursor.fetchone()
      self.assertIsNotNone(result)
      self.assertEqual(result['ps_lang'], b'en')
      self.assertEqual(result['ps_article'], b'Statue_of_Liberty')
      self.assertEqual(result['ps_page_id'], 1234)
      self.assertEqual(result['ps_views'], 100)

  def test_update_db_pageviews_existing(self):
    with self.wp10db.cursor() as cursor:
      cursor.execute(
          'INSERT INTO page_scores (ps_lang, ps_article, ps_page_id, ps_views) '
          'VALUES ("en", "Statue_of_Liberty", 1234, 100)')

    scores.update_db_pageviews(self.wp10db, 'en', 'Statue_of_Liberty', 1234,
                               200)

    with self.wp10db.cursor() as cursor:
      cursor.execute('SELECT * FROM page_scores WHERE ps_page_id = 1234')
      result = cursor.fetchone()
      self.assertIsNotNone(result)
      self.assertEqual(result['ps_lang'], b'en')
      self.assertEqual(result['ps_article'], b'Statue_of_Liberty')
      self.assertEqual(result['ps_page_id'], 1234)
      self.assertEqual(result['ps_views'], 200)

  @patch('wp1.scores.download_pageviews')
  @patch('wp1.scores.pageview_components')
  def test_update_pageviews(self, mock_components, mock_download):
    mock_components.return_value = (
        (b'en', b'Statue_of_Liberty', 100, 100),
        (b'en', b'Eiffel_Tower', 200, 200),
        (b'fr', b'George-\xc3\x89tienne_Cartier_Monument', 300, 300),
    )

    scores.update_pageviews(commit_after=2)

    mock_download.assert_called_once()
    with self.wp10db.cursor() as cursor:
      cursor.execute('SELECT COUNT(*) as cnt FROM page_scores')
      n = cursor.fetchone()['cnt']
      self.assertEqual(3, n)

  @patch('wp1.scores.download_pageviews')
  @patch('wp1.scores.pageview_components')
  def test_update_pageviews_filter(self, mock_components, mock_download):
    mock_components.return_value = (
        (b'en', b'Statue_of_Liberty', 100, 100),
        (b'en', b'Eiffel_Tower', 200, 200),
        (b'fr', b'George-\xc3\x89tienne_Cartier_Monument', 300, 300),
    )

    scores.update_pageviews(filter_lang='fr')

    mock_download.assert_called_once()
    with self.wp10db.cursor() as cursor:
      cursor.execute('SELECT COUNT(*) as cnt FROM page_scores')
      n = cursor.fetchone()['cnt']
      self.assertEqual(1, n)
