import json
import logging
from datetime import timedelta

import mwclient
from redis import Redis

from wp1.api import MW_USER_AGENT

logger = logging.getLogger(__name__)

CACHE_KEY = "site_data"
CACHE_TTL = timedelta(days=1)


def _fetch_site_data() -> dict:
    """Fetches the sitematrix from meta.wikimedia.org.

    Returns a dict with 'projects', the ordered list of language project
    domains (eg 'en.wikipedia.org'), and 'dbnames', a mapping of every site
    domain (including specials) to its database name (eg 'enwiki').
    """
    site = mwclient.Site("meta.wikimedia.org", clients_useragent=MW_USER_AGENT)
    sitematrix = site.api("sitematrix")["sitematrix"]

    projects = []
    dbnames = {}
    for key, value in sitematrix.items():
        if key == "count":
            continue
        sites = value if key == "specials" else value["site"]
        for s in sites:
            domain = s["url"].replace("https://", "")
            dbnames[domain] = s["dbname"]
            if key != "specials":
                projects.append(domain)

    return {"projects": projects, "dbnames": dbnames}


def get_site_data(redis: Redis) -> dict:
    """Returns the sitematrix data, from the redis cache if possible."""
    raw = redis.get(CACHE_KEY)
    if raw is not None:
        try:
            return json.loads(raw)
        except ValueError:
            logger.warning("Discarding unparseable cached site data")
    data = _fetch_site_data()
    redis.setex(CACHE_KEY, CACHE_TTL, value=json.dumps(data))
    return data


def get_projects(redis: Redis) -> list[str]:
    """Returns the list of language project domains, eg 'en.wikipedia.org'."""
    return get_site_data(redis)["projects"]


def dbname_for_project(redis: Redis, project: str) -> str | None:
    """Returns the dbname (eg 'enwiki') for a project domain, or None."""
    return get_site_data(redis)["dbnames"].get(project)
