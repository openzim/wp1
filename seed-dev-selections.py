"""Seeds the dev database with test Selection data for the dev user.

Inserts a set of builders/selections/zim_tasks covering every status that
the Selections screens can render (processing, failed, building, up to
date, stale, expired, no ZIM), across all builder models. The rows belong
to the fake development user (``dev_user_12345``) that the dev environment
logs you in as, so after running this script the data is visible at
http://localhost:5173/#/selections/user after clicking "Login".

The script connects directly to the dev database from docker-compose-dev.yml
and is idempotent: seeded rows all have ids prefixed with ``dev-seed-`` and
are deleted and re-created on every run.

Usage:

    pipenv run python seed-dev-selections.py
"""

import argparse
import json
import logging
import uuid
from datetime import datetime, timedelta, timezone

import pymysql

logger = logging.getLogger(__name__)

TS_FORMAT_WP10 = "%Y%m%d%H%M%S"

DEV_USER_ID = "dev_user_12345"
DEV_USERNAME = "dev_user"

TSV = "text/tab-separated-values"

SIMPLE = "wp1.selection.models.simple"
SPARQL = "wp1.selection.models.sparql"
PETSCAN = "wp1.selection.models.petscan"
BOOK = "wp1.selection.models.book"
WIKIPROJECT = "wp1.selection.models.wikiproject"
COMBINATOR = "wp1.selection.models.combinator"

NOW = datetime.now(timezone.utc)


def ts(dt):
    return dt.strftime(TS_FORMAT_WP10).encode("utf-8")


def days_ago(days, minutes=0):
    return NOW - timedelta(days=days, minutes=minutes)


# Each entry becomes one builder row, plus optionally a selection row, a
# zim_tasks row and a zim_schedules row. Timestamps are datetimes; None
# means "no row". The b_id/s_id values are stable so that re-running the
# script replaces the same rows.
SEED_BUILDERS = [
    {
        # Selection OK, recent ZIM file -> "Up to date". Also has an active
        # schedule, so the detail pane shows the recurring generation info.
        "id": "dev-seed-simple-uptodate",
        "name": "US national parks",
        "project": "en.wikipedia.org",
        "model": SIMPLE,
        "params": {
            "list": [
                "Yellowstone_National_Park",
                "Yosemite_National_Park",
                "Grand_Canyon_National_Park",
                "Zion_National_Park",
                "Acadia_National_Park",
            ]
        },
        "created_at": days_ago(40),
        "updated_at": days_ago(2, minutes=10),
        "selection": {"updated_at": days_ago(2), "article_count": 5},
        "zim": {"status": "FILE_READY", "updated_at": days_ago(1)},
        "schedule": {
            "interval": 30,
            "remaining_generations": 3,
            "title": "US national parks",
            "description": "The most visited US national parks",
        },
    },
    {
        # Selection OK, ZIM never requested -> "No ZIM".
        "id": "dev-seed-sparql-nozim",
        "name": "Women Nobel laureates",
        "project": "en.wikipedia.org",
        "model": SPARQL,
        "params": {
            "query": (
                "SELECT ?article WHERE {\n"
                "  ?person wdt:P166 wd:Q35637 ;\n"
                "          wdt:P21 wd:Q6581072 .\n"
                "  ?article schema:about ?person ;\n"
                "           schema:isPartOf <https://en.wikipedia.org/> .\n"
                "}"
            ),
            "queryVariable": "article",
        },
        "created_at": days_ago(25),
        "updated_at": days_ago(5, minutes=10),
        "selection": {"updated_at": days_ago(5), "article_count": 65},
    },
    {
        # ZIM file older than the current selection -> "Stale".
        "id": "dev-seed-petscan-stale",
        "name": "Films set in Paris",
        "project": "en.wikipedia.org",
        "model": PETSCAN,
        "params": {"url": "https://petscan.wmcloud.org/?psid=24880"},
        "created_at": days_ago(60),
        "updated_at": days_ago(1, minutes=10),
        "selection": {"updated_at": days_ago(1), "article_count": 312},
        "zim": {"status": "FILE_READY", "updated_at": days_ago(4)},
    },
    {
        # ZIM file past the two week retention window -> "Expired".
        "id": "dev-seed-book-expired",
        "name": "Solar System reader",
        "project": "en.wikipedia.org",
        "model": BOOK,
        "params": {"url": "https://en.wikipedia.org/wiki/Book:Solar_System"},
        "created_at": days_ago(90),
        "updated_at": days_ago(30, minutes=10),
        "selection": {"updated_at": days_ago(30), "article_count": 44},
        "zim": {"status": "FILE_READY", "updated_at": days_ago(29)},
    },
    {
        # ZIM requested and still in the Zimfarm queue -> "Building".
        "id": "dev-seed-wikiproject-building",
        "name": "Chemistry articles",
        "project": "en.wikipedia.org",
        "model": WIKIPROJECT,
        "params": {"include": ["Chemistry"], "exclude": ["Physics"]},
        "created_at": days_ago(10),
        "updated_at": days_ago(3, minutes=10),
        "selection": {"updated_at": days_ago(3), "article_count": 8125},
        "zim": {"status": "REQUESTED", "updated_at": days_ago(0, minutes=20)},
    },
    {
        # Combinator over two of the other seeded selections, with a recent
        # ZIM -> "Up to date". Exercises the include/exclude recipe UI.
        "id": "dev-seed-combinator-uptodate",
        "name": "Parks and Paris films",
        "project": "en.wikipedia.org",
        "model": COMBINATOR,
        "params": {
            "include": {
                "builders": ["dev-seed-simple-uptodate", "dev-seed-petscan-stale"],
                "operation": "union",
            },
            "exclude": {
                "builders": ["dev-seed-sparql-nozim"],
                "operation": "union",
            },
        },
        "created_at": days_ago(15),
        "updated_at": days_ago(6, minutes=10),
        "selection": {"updated_at": days_ago(6), "article_count": 298},
        "zim": {"status": "FILE_READY", "updated_at": days_ago(5)},
    },
    {
        # Builder saved but the selection list has not materialized yet
        # -> "Processing".
        "id": "dev-seed-simple-processing",
        "name": "Basic English vocabulary",
        "project": "en.wiktionary.org",
        "model": SIMPLE,
        "params": {"list": ["water", "fire", "earth", "air"]},
        "created_at": days_ago(0, minutes=5),
        "updated_at": days_ago(0, minutes=5),
    },
    {
        # Materialization failed with a retryable error -> "Failed", with
        # a Retry button in the detail pane.
        "id": "dev-seed-sparql-retryable",
        "name": "Paintings in the Louvre",
        "project": "en.wikipedia.org",
        "model": SPARQL,
        "params": {
            "query": (
                "SELECT ?article WHERE {\n"
                "  ?painting wdt:P276 wd:Q19675 .\n"
                "  ?article schema:about ?painting .\n"
                "}"
            ),
            "queryVariable": "article",
        },
        "created_at": days_ago(8),
        "updated_at": days_ago(2, minutes=10),
        "selection": {
            "updated_at": days_ago(2),
            "status": "CAN_RETRY",
            "error_messages": [
                "The SPARQL endpoint returned a server error (HTTP 500)",
                "This is usually temporary. Retrying may fix the problem.",
            ],
        },
    },
    {
        # Materialization failed permanently -> "Failed", no Retry button.
        "id": "dev-seed-petscan-fatal",
        "name": "Deleted Petscan query",
        "project": "en.wikipedia.org",
        "model": PETSCAN,
        "params": {"url": "https://petscan.wmcloud.org/?psid=999999999"},
        "created_at": days_ago(20),
        "updated_at": days_ago(7, minutes=10),
        "selection": {
            "updated_at": days_ago(7),
            "status": "FAILED",
            "error_messages": [
                "The Petscan server did not return any data for PSID 999999999",
                "The saved query may have been deleted from Petscan",
            ],
        },
    },
    {
        # The Zimfarm build failed -> "Failed" (ZIM error, selection OK).
        "id": "dev-seed-simple-zimfailed",
        "name": "Endangered languages",
        "project": "en.wikipedia.org",
        "model": SIMPLE,
        "params": {
            "list": [
                "Ainu_language",
                "Livonian_language",
                "Manx_language",
                "Yuchi_language",
            ]
        },
        "created_at": days_ago(12),
        "updated_at": days_ago(4, minutes=10),
        "selection": {"updated_at": days_ago(4), "article_count": 4},
        "zim": {"status": "FAILED", "updated_at": days_ago(3)},
    },
]


def delete_existing(cursor):
    cursor.execute("DELETE FROM zim_tasks WHERE z_selection_id LIKE 'dev-seed-%'")
    cursor.execute("DELETE FROM zim_schedules WHERE s_builder_id LIKE 'dev-seed-%'")
    cursor.execute("DELETE FROM selections WHERE s_builder_id LIKE 'dev-seed-%'")
    cursor.execute("DELETE FROM builders WHERE b_id LIKE 'dev-seed-%'")


def insert_user(cursor):
    cursor.execute(
        """INSERT INTO users (u_id, u_username, u_email)
           VALUES (%s, %s, %s)
           ON DUPLICATE KEY UPDATE u_username = VALUES(u_username)""",
        (DEV_USER_ID, DEV_USERNAME, "dev_user@example.com"),
    )


def insert_builder(cursor, spec):
    selection = spec.get("selection")
    # Builders whose materialization failed never get a ZIM-able version.
    selection_ok = selection is not None and "status" not in selection
    cursor.execute(
        """INSERT INTO builders
           (b_id, b_name, b_user_id, b_project, b_model, b_params,
            b_created_at, b_updated_at, b_current_version,
            b_selection_zim_version)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            spec["id"].encode("utf-8"),
            spec["name"].encode("utf-8"),
            DEV_USER_ID,
            spec["project"].encode("utf-8"),
            spec["model"].encode("utf-8"),
            json.dumps(spec["params"]).encode("utf-8"),
            ts(spec["created_at"]),
            ts(spec["updated_at"]),
            1 if selection else 0,
            1 if selection_ok else 0,
        ),
    )

    if selection is None:
        return

    selection_id = "%s-sel" % spec["id"]
    error_messages = None
    if "error_messages" in selection:
        error_messages = json.dumps(
            {"error_messages": selection["error_messages"]}
        ).encode("utf-8")
    cursor.execute(
        """INSERT INTO selections
           (s_id, s_builder_id, s_content_type, s_updated_at, s_version,
            s_object_key, s_status, s_error_messages, s_article_count)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            selection_id.encode("utf-8"),
            spec["id"].encode("utf-8"),
            TSV.encode("utf-8"),
            ts(selection["updated_at"]),
            1,
            ("selections/%s/1/%s.tsv" % (spec["model"], spec["id"])).encode("utf-8"),
            selection.get("status", "OK").encode("utf-8"),
            error_messages,
            selection.get("article_count"),
        ),
    )

    zim = spec.get("zim")
    if zim is not None:
        cursor.execute(
            """INSERT INTO zim_tasks
               (z_selection_id, z_status, z_task_id, z_requested_at,
                z_updated_at)
               VALUES (%s, %s, %s, %s, %s)""",
            (
                selection_id.encode("utf-8"),
                zim["status"].encode("utf-8"),
                str(uuid.uuid4()).encode("utf-8"),
                ts(zim["updated_at"] - timedelta(hours=1)),
                ts(zim["updated_at"]),
            ),
        )

    schedule = spec.get("schedule")
    if schedule is not None:
        cursor.execute(
            """INSERT INTO zim_schedules
               (s_id, s_builder_id, s_interval, s_remaining_generations,
                s_last_updated_at, s_title, s_description)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                ("%s-sched" % spec["id"]).encode("utf-8")[:36],
                spec["id"].encode("utf-8"),
                schedule["interval"],
                schedule["remaining_generations"],
                ts(spec["updated_at"]),
                schedule["title"].encode("utf-8"),
                schedule["description"].encode("utf-8"),
            ),
        )


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(
        description="Seed the dev database with test Selection data"
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=6300)
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="wikipedia")
    parser.add_argument("--database", default="enwp10_dev")
    args = parser.parse_args()

    wp10db = pymysql.connect(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        db=args.database,
        charset=None,
        use_unicode=False,
    )

    try:
        with wp10db.cursor() as cursor:
            delete_existing(cursor)
            insert_user(cursor)
            for spec in SEED_BUILDERS:
                logger.info("Seeding builder %s (%s)", spec["id"], spec["name"])
                insert_builder(cursor, spec)
        wp10db.commit()
    finally:
        wp10db.close()

    logger.info(
        "Done. Log in as the dev user and visit "
        "http://localhost:5173/#/selections/user"
    )


if __name__ == "__main__":
    main()
