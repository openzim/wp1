import unittest
from unittest.mock import patch, MagicMock

import requests

from wp1.exceptions import Wp1ScoreProcessingError
from wp1.scores import wiki_languages


class ScoresTest(unittest.TestCase):

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

    actual = list(wiki_languages())
    self.assertEqual(['en', 'ceb', 'de', 'fr'], actual)

  @patch('wp1.scores.requests')
  def test_wiki_languages_raises_on_http_error(self, mock_requests):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
    mock_requests.exceptions.HTTPError = requests.exceptions.HTTPError
    mock_requests.get.return_value = mock_response

    with self.assertRaises(Wp1ScoreProcessingError):
      list(wiki_languages())
