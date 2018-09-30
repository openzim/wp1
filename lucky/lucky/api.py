import mwclient

from lucky.credentials import API_CREDS

_ua = 'WP1.0Bot/3.0. Run by User:Audiodude. Using mclient/0.9.1'
site = mwclient.Site('en.wikipedia.org',
                     clients_useragent=_ua,
                     consumer_token=API_CREDS['CONSUMER_TOKEN'],
                     consumer_secret=API_CREDS['CONSUMER_SECRET'],
                     access_token=API_CREDS['ACCESS_TOKEN'],
                     access_secret=API_CREDS['ACCESS_SECRET'])
