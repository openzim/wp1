import logging
import pickle
from datetime import datetime, timedelta

from wp1 import api, app_logging
from wp1.redis_db import connect as redis_connect
from wp1.templates import env as jinja_env
from wp1.wiki_db import connect as wiki_connect
from wp1.wp10_db import connect as wp10_connect

logger = logging.getLogger(__name__)

BACKLOG_KEY = "wp1:npp:backlog"
BATCH_SIZE = 1000


def npp_page_name(project_name):
    return "User:WP 1.0 bot/Tables/Project/%s/NPP" % project_name.decode("utf-8")


def fetch_backlog(wikidb):
    wikidb.ping()
    with wikidb.cursor() as cursor:
        cursor.execute("""
          SELECT p.page_title, ptrp.ptrp_created
          FROM pagetriage_page ptrp
          JOIN page p ON p.page_id = ptrp.ptrp_page_id
          WHERE ptrp.ptrp_reviewed = 0
            AND p.page_namespace = 0
            AND p.page_is_redirect = 0
        """)
        return {row["page_title"]: row["ptrp_created"] for row in cursor.fetchall()}


def get_backlog(redis, wikidb):
    pkl = redis.get(BACKLOG_KEY)
    if pkl is not None:
        return pickle.loads(pkl)  # nosec

    backlog = fetch_backlog(wikidb)
    redis.setex(BACKLOG_KEY, timedelta(hours=1), value=pickle.dumps(backlog))
    return backlog


def get_project_articles(wp10db, project_name, backlog):
    titles = list(backlog)
    articles = []
    wp10db.ping()
    with wp10db.cursor() as cursor:
        for i in range(0, len(titles), BATCH_SIZE):
            batch = titles[i : i + BATCH_SIZE]
            cursor.execute(
                """
              SELECT r_article, r_quality, r_importance FROM ratings
              WHERE r_project = %s AND r_namespace = 0 AND r_article IN %s
            """,
                (project_name, batch),
            )
            for row in cursor.fetchall():
                articles.append(
                    {
                        "title": row["r_article"].decode("utf-8").replace("_", " "),
                        "created": datetime.strptime(
                            backlog[row["r_article"]].decode("utf-8"), "%Y%m%d%H%M%S"
                        ),
                        "quality": row["r_quality"],
                        "importance": row["r_importance"],
                    }
                )
    return sorted(articles, key=lambda a: (a["created"], a["title"]))


def create_wikicode(project_name, articles):
    template = jinja_env.get_template("npp.jinja2")
    return template.render(
        project=project_name.decode("utf-8").replace("_", " "), articles=articles
    )


def upload_project_npp_table(project_name):
    app_logging.configure_logging()
    wikidb = wiki_connect()
    wp10db = wp10_connect()
    redis = redis_connect()

    try:
        backlog = get_backlog(redis, wikidb)
        articles = get_project_articles(wp10db, project_name, backlog)

        page = api.get_page(npp_page_name(project_name))
        if page is None:
            return
        if not articles and not page.exists:
            logger.info(
                "No NPP articles for %s, not creating a page",
                project_name.decode("utf-8"),
            )
            return

        logger.info("Uploading NPP table for %s", project_name.decode("utf-8"))
        api.save_page(
            page,
            create_wikicode(project_name, articles),
            "Update New Pages Patrol article list.",
        )
    finally:
        if wikidb:
            wikidb.close()
        if wp10db:
            wp10db.close()
