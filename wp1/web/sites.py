import flask
import mwclient
from datetime import timedelta
from wp1.web.redis import get_redis

sites = flask.Blueprint('sites', __name__)
_ua = 'WP1.0Bot/3.0. Run by User:Audiodude. Using mwclient/0.9.1'


@sites.route('/')
def get_sites():
  redis = get_redis()
  if redis.get('sites'):
    return {'data': redis.get('sites').decode('utf-8').split(',')}

  site = mwclient.Site('meta.wikimedia.org', clients_useragent=_ua)
  result = site.api('sitematrix')
  response = []
  result['sitematrix'].pop('specials')
  result['sitematrix'].pop('count')

  for i in result['sitematrix']:
    for j in result['sitematrix'][i]['site']:
      response.append(j['url'])

  redis.setex('sites', timedelta(days=1), value=','.join(response))
  return {'data': response}
