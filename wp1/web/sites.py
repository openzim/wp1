import flask
import mwclient
from datetime import timedelta
from wp1.api import MW_USER_AGENT
from wp1.web.redis import get_redis

sites = flask.Blueprint('sites', __name__)
site = None


@sites.route('/')
def get_sites():
  redis = get_redis()
  sites_data = redis.get('sites')
  if sites_data is not None:
    return {'sites': sites_data.decode('utf-8').split(',')}

  site = mwclient.Site('meta.wikimedia.org', clients_useragent=MW_USER_AGENT)
  sitematrix = site.api('sitematrix')['sitematrix']
  sitematrix.pop('specials')
  sitematrix.pop('count')

  sites_data = []
  for i in sitematrix:
    for j in sitematrix[i]['site']:
      project = j['url'].replace('https://', '')
      sites_data.append(project)

  redis.setex('sites_data', timedelta(days=1), value=','.join(sites_data))
  return {'sites': sites_data}
