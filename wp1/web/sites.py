import flask

import wp1.logic.sites as logic_sites
from wp1.web.redis import get_redis

sites = flask.Blueprint("sites", __name__)


@sites.route("/")
def get_sites():
    return {"sites": logic_sites.get_projects(get_redis())}
