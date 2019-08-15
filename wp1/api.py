import mwclient

_ua = 'WP1.0Bot/3.0. Run by User:Audiodude. Using mwclient/0.9.1'

try:
  from wp1.credentials import API_CREDS
  site = mwclient.Site('en.wikipedia.org',
                       clients_useragent=_ua)
  site.login(API_CREDS['user'], API_CREDS['pass'])
except ImportError:
  site = None
