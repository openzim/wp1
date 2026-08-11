"""Seeds the dev database with test Selection data for the dev user.

Inserts a set of builders/selections/zim_tasks covering every status that
the Selections screens can render (processing, failed, building, up to
date, stale, expired, no ZIM), across all builder models. The rows belong
to the fake development user (``dev_user_12345``) that the dev environment
logs you in as when no OAuth credentials are configured, so after running
this script the data is visible at http://localhost:5173/#/selections/user
after clicking "Login".

If your credentials.py.dev has real MWOAUTH credentials, you log in as your
actual Wikipedia user instead; pass that user's id to seed the same data for
it (find it with ``SELECT u_id, u_username FROM users``):

    pipenv run python seed-dev-selections.py --user-id 12345678 --username You

The script connects directly to the dev database from docker-compose-dev.yml
and is idempotent: seeded rows all have ids prefixed with ``dev-seed-`` and
the target user's seeded rows are deleted and re-created on every run.

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
# means "no row". The "id" slugs become stable per-user row ids
# (dev-seed-<user_id>-<slug>), so re-running the script replaces the same
# rows; combinator params reference other entries by slug.
SEED_BUILDERS = [
    {
        # Selection OK, recent ZIM file -> "Up to date". Also has an active
        # schedule, so the detail pane shows the recurring generation info.
        "id": "simple-uptodate",
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
        "id": "sparql-nozim",
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
        "id": "petscan-stale",
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
        "id": "book-expired",
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
        "id": "wikiproject-building",
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
        "id": "combinator-uptodate",
        "name": "Parks and Paris films",
        "project": "en.wikipedia.org",
        "model": COMBINATOR,
        "params": {
            "include": {
                "builders": ["simple-uptodate", "petscan-stale"],
                "operation": "union",
            },
            "exclude": {
                "builders": ["sparql-nozim"],
                "operation": "union",
            },
        },
        "created_at": days_ago(15),
        "updated_at": days_ago(6, minutes=10),
        "selection": {"updated_at": days_ago(6), "article_count": 298},
        "zim": {"status": "FILE_READY", "updated_at": days_ago(5)},
    },
    {
        # A second combinator sharing "petscan-stale" with the first one
        # (Comb 1 -> A+B, Comb 2 -> B+C), so deleting the shared selection
        # shows delete-impact warnings for both combinators. No ZIM.
        "id": "combinator-nozim",
        "name": "Paris films plus Solar System",
        "project": "en.wikipedia.org",
        "model": COMBINATOR,
        "params": {
            "include": {
                "builders": ["petscan-stale", "book-expired"],
                "operation": "union",
            },
        },
        "created_at": days_ago(9),
        "updated_at": days_ago(2, minutes=15),
        "selection": {"updated_at": days_ago(2, minutes=5), "article_count": 356},
    },
    {
        # Builder saved but the selection list has not materialized yet
        # -> "Processing".
        "id": "simple-processing",
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
        "id": "sparql-retryable",
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
        "id": "petscan-fatal",
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
        "id": "simple-zimfailed",
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


def full_id(user_id, slug):
    return "dev-seed-%s-%s" % (user_id, slug)


def delete_existing(cursor, user_id):
    cursor.execute(
        """DELETE z FROM zim_tasks z
           JOIN selections s ON z.z_selection_id = s.s_id
           JOIN builders b ON s.s_builder_id = b.b_id
           WHERE b.b_user_id = %s AND b.b_id LIKE 'dev-seed-%%'""",
        (user_id,),
    )
    cursor.execute(
        """DELETE zs FROM zim_schedules zs
           JOIN builders b ON zs.s_builder_id = b.b_id
           WHERE b.b_user_id = %s AND b.b_id LIKE 'dev-seed-%%'""",
        (user_id,),
    )
    cursor.execute(
        """DELETE s FROM selections s
           JOIN builders b ON s.s_builder_id = b.b_id
           WHERE b.b_user_id = %s AND b.b_id LIKE 'dev-seed-%%'""",
        (user_id,),
    )
    cursor.execute(
        "DELETE FROM builders WHERE b_user_id = %s AND b_id LIKE 'dev-seed-%%'",
        (user_id,),
    )


def insert_user(cursor, user_id, username):
    email = "dev_user@example.com" if user_id == DEV_USER_ID else None
    cursor.execute(
        """INSERT INTO users (u_id, u_username, u_email)
           VALUES (%s, %s, %s)
           ON DUPLICATE KEY UPDATE u_username = VALUES(u_username)""",
        (user_id, username, email),
    )


def builder_params(spec, user_id):
    if spec["model"] != COMBINATOR:
        return spec["params"]
    # Combinator params reference other seed entries by slug; expand them
    # to the full per-user builder ids.
    params = {}
    for group_name, group in spec["params"].items():
        params[group_name] = {
            "builders": [full_id(user_id, slug) for slug in group["builders"]],
            "operation": group["operation"],
        }
    return params


def insert_builder(cursor, spec, user_id):
    builder_id = full_id(user_id, spec["id"])
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
            builder_id.encode("utf-8"),
            spec["name"].encode("utf-8"),
            user_id,
            spec["project"].encode("utf-8"),
            spec["model"].encode("utf-8"),
            json.dumps(builder_params(spec, user_id)).encode("utf-8"),
            ts(spec["created_at"]),
            ts(spec["updated_at"]),
            1 if selection else 0,
            1 if selection_ok else 0,
        ),
    )

    if selection is None:
        return

    selection_id = "%s-sel" % builder_id
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
            builder_id.encode("utf-8"),
            TSV.encode("utf-8"),
            ts(selection["updated_at"]),
            1,
            ("selections/%s/1/%s.tsv" % (spec["model"], builder_id)).encode("utf-8"),
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
                # zim_schedules ids are varbinary(36), sized for a UUID, so
                # a stable readable id does not fit here.
                str(uuid.uuid4()).encode("utf-8"),
                builder_id.encode("utf-8"),
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
    parser.add_argument(
        "--user-id",
        default=DEV_USER_ID,
        help="The users.u_id to attach the seeded selections to. Defaults to "
        "the fake dev user that the dev environment logs you in as when no "
        "OAuth credentials are configured.",
    )
    parser.add_argument(
        "--username",
        default=None,
        help="The username for --user-id. Required when --user-id is given.",
    )
    args = parser.parse_args()

    if args.user_id != DEV_USER_ID and args.username is None:
        parser.error("--username is required when --user-id is given")
    username = args.username or DEV_USERNAME

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
            delete_existing(cursor, args.user_id)
            insert_user(cursor, args.user_id, username)
            for spec in SEED_BUILDERS:
                logger.info(
                    "Seeding builder %s (%s)",
                    full_id(args.user_id, spec["id"]),
                    spec["name"],
                )
                insert_builder(cursor, spec, args.user_id)
        wp10db.commit()
    finally:
        wp10db.close()

    logger.info(
        "Done. Log in as %s and visit http://localhost:5173/#/selections/user",
        username,
    )


if __name__ == "__main__":
    main()
