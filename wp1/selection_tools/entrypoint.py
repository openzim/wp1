from collections import defaultdict
from typing import TYPE_CHECKING
import time
import subprocess
from concurrent.futures import as_completed
from concurrent.futures.process import ProcessPoolExecutor
import shutil
from pymysql import Connection
from wp1.scores import get_wiki_languages_exceeding_count
from wp1.selection_tools.constants import BASE_DIR, DATA_DIR
from wp1.selection_tools.custom import build_custom_selections
from wp1.selection_tools.projects_list import build_translated_list
import pathlib
from wp1.selection_tools.projects_list import build_langlinks
from wp1.selection_tools.scores import generate_scores
from wp1.wp10_db import connect as wp10_connect
from wp1.selection_tools import write_tsv_rows_to_file
from wp1.selection_tools.wiki.en import (
    build_projects_list as build_enwiki_projects_list,
)
from wp1 import wikilang_db
from wp1.selection_tools.wiki.en import get_vital_articles
import argparse
import logging

if TYPE_CHECKING:
    from pymysql.cursors import Cursor

from typing import NamedTuple

from wp1.time import get_current_datetime

logger = logging.getLogger(__name__)

CHUNK_SIZE = 8 * 1024 * 1024  # chunk size for downloads


def _fetch_paginated_rows_from_db(
    conn: "Connection[Cursor]", statement: str, batch_size: int
):
    """Fetch rows from a range query, stopping when a batch is empty."""
    lower = 0
    with conn.cursor() as cursor:
        while True:
            upper = lower + batch_size
            cursor.execute(statement, (lower, upper))
            rows = cursor.fetchall()
            if not rows:
                break
            yield from rows
            lower = upper


def _fetch_ratings_from_db(conn: "Connection[Cursor]"):
    stmt = """
    SELECT r_article, r_project, r_quality, r_importance
    FROM ratings
    """
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT DISTINCT r_importance FROM ratings where r_importance IS NOT NULL"
        )
        importances = [row[0] for row in cursor.fetchall()]
        for importance in importances:
            logger.info(f"Gathering ratings with importance {importance}...")
            cursor.execute(stmt + " WHERE r_importance = %s", (importance,))
            while True:
                rows = cursor.fetchmany(10_000)
                if not rows:
                    break
                yield from rows

        logger.info("Gathering ratings with importance IS NULL...")
        cursor.execute(stmt + " WHERE r_importance IS NULL")
        while True:
            rows = cursor.fetchmany(10_000)
            if not rows:
                break
            yield from rows


def _fetch_pageviews_from_db(conn: "Connection[Cursor]", lang_code: str):
    """Yield (article, views) from the WP1 engine's page_scores table."""
    stmt = """
    SELECT ps_article, ps_views
    FROM page_scores
    WHERE ps_lang = %s AND ps_views > 0
    ORDER BY ps_article
    """
    with conn.cursor() as cursor:
        cursor.execute(stmt, (lang_code,))
        while True:
            rows = cursor.fetchmany(10_000)
            if not rows:
                break
            yield from rows


def _fetch_langlinks_from_db(conn: "Connection[Cursor]"):
    stmt = """
    SELECT page_title, ll_lang, ll_title
    FROM langlinks, page
    WHERE langlinks.ll_from = page.page_id AND page.page_namespace = 0
    """
    with conn.cursor() as cursor:
        cursor.execute(stmt)
        while True:
            rows = cursor.fetchmany(10_000)
            if not rows:
                break
            for row in rows:
                # Replace spaces with underscores
                yield tuple(
                    col.replace(" ", "_") if isinstance(col, str) else col
                    for col in row
                )


def _merge_rows(
    pages_fp: pathlib.Path,
    pageviews_fp: pathlib.Path,
    ratings_fp: pathlib.Path,
):
    """Merge the generated TSV files and write to dest"""
    counts = defaultdict(dict)
    id_to_title: dict[int, str] = {}

    with pages_fp.open(encoding="utf-8") as f:
        for line in f:
            page_id, title, size, is_redirect = line.rstrip("\n").split("\t")
            page_id = int(page_id)
            is_redirect = int(is_redirect)

            counts[title]["i"] = page_id
            if not is_redirect:
                counts[title]["s"] = int(size)
            id_to_title[page_id] = title

    with pageviews_fp.open(encoding="utf-8") as f:
        for line in f:
            title, views = line.rstrip("\n").split("\t")
            counts[title]["v"] = int(views)

    if ratings_fp.exists():
        with ratings_fp.open(encoding="utf-8") as f:
            for line in f:
                title, project, quality, importance = line.rstrip("\n").split("\t")
                counts[title].setdefault("r", []).append(
                    f"{project}={quality}:{importance}"
                )

    with pages_fp.open(encoding="utf-8") as f:
        for line in f:
            page_id, title, size, is_redirect = line.rstrip("\n").split("\t")
            if int(is_redirect):
                continue
            count = counts[title]
            row = [
                title,
                count.get("i", page_id),
                count.get("s", 0),
                count.get("l", 0),
                count.get("ll", 0),
                count.get("v", 0),
            ]
            row += count.get("r", [])
            yield row


def build_top_selections(scores_fp: pathlib.Path, tops_dir: pathlib.Path) -> None:
    tops_dir.mkdir(exist_ok=True)

    tops = [10, 50, 100, 500, 1000, 5000, 10_000, 50_000, 100_000, 500_000, 1000_000]
    max_top = max(tops)
    titles: list[str] = []
    total = 0
    with scores_fp.open(encoding="utf-8") as f:
        for line in f:
            if total < max_top:
                titles.append(line.split("\t", 1)[0])
            total += 1

    for top in tops:
        if total > top:
            (tops_dir / f"{top}.tsv").write_text(
                "\n".join(titles[:top]) + "\n", encoding="utf-8"
            )
        else:
            break


def _zip_file(fp: pathlib.Path) -> None:
    """Compress ``fp`` with 7-Zip and remove the original."""
    subprocess.run(["7za", "a", "-tzip", f"{fp}.zip", str(fp)], check=True)

    if fp.is_dir():
        shutil.rmtree(fp)
    else:
        fp.unlink()


def _compress_all(base_dir: pathlib.Path) -> None:
    entries = [
        path
        for path in base_dir.iterdir()
        if path.name != "README" and not path.name.endswith(".zip")
    ]

    with ProcessPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(_zip_file, path) for path in entries]
        for future in futures:
            future.result()


class RemoteConfig(NamedTuple):
    host: str
    port: str
    path: str


def _parse_remote_config(text: str) -> RemoteConfig:
    text = text.strip()
    if "::" in text:
        host, _, path = text.split(":", 2)
        return RemoteConfig(host=host, port="22", path=path)
    host, port, path = text.split(":", 2)
    return RemoteConfig(host=host, port=port, path=path)


def _upload_dir(base_dir: pathlib.Path) -> None:
    remote = (BASE_DIR / "remote").read_text(encoding="utf-8").strip()
    config = _parse_remote_config(remote)
    logger.info(f"Uploading {base_dir} to {config.host} on port {config.port}")

    for name in ("customs.zip", "tops.zip", "projects.zip"):
        zip_path = base_dir / name
        if zip_path.exists():
            subprocess.run(
                ["unzip", "-UU", "-o", "-d", str(base_dir), str(zip_path)],
                check=True,
            )

    subprocess.run(
        [
            "scp",
            "-P",
            config.port,
            "-o",
            "StrictHostKeyChecking=no",
            "-r",
            str(base_dir),
            f"{config.host}:{config.path}",
        ],
        check=True,
    )


def build_selections(lang_code: str, data_dir: pathlib.Path):
    wikidb = wikilang_db.connect(lang_code)
    wp10db = wp10_connect()
    wikidb.ping()
    wp10db.ping()

    wiki = f"{lang_code}wiki"

    # Create directories for storing artifacts
    tmp_dir = data_dir / "tmp"
    lang_dir = tmp_dir / (wiki + "_" + get_current_datetime().strftime("%Y-%m"))
    tmp_dir.mkdir(parents=True, exist_ok=True)
    lang_dir.mkdir(parents=True, exist_ok=True)
    readme_fp = lang_dir / "README"
    readme_lines: list[str] = []

    ######################################################################
    # GATHER PAGES KEYS VALUES                                           #
    ######################################################################

    ## Pages
    logger.info("Gathering pageviews....")
    readme_lines.append("pageviews.tsv: page_title view_count\n")
    pageviews_tsv_fp = lang_dir / "pageviews.tsv"
    with pageviews_tsv_fp.open("w", encoding="utf-8") as f:
        write_tsv_rows_to_file(f, _fetch_pageviews_from_db(wp10db, lang_code))

    logger.info("Gathering pages...")
    readme_lines.append("pages.tsv: page_id page_title page_size\n")

    pages_tsv_fp = lang_dir / "pages.tsv"
    pages_sql = """
    SELECT page.page_id, page.page_title, revision.rev_len
    FROM page
    JOIN revision ON revision.rev_id = page.page_latest
    WHERE page.page_namespace = 0
      AND page.page_id >= %s AND page.page_id < %s
    """
    with pages_tsv_fp.open("w", encoding="utf-8") as f:
        write_tsv_rows_to_file(
            f, _fetch_paginated_rows_from_db(wikidb, pages_sql, 100_000)
        )

    ######################################################################
    # GATHER WP1 RATINGS FOR WPEN                                        #
    ######################################################################

    ratings_tsv_fp = lang_dir / "ratings.tsv"
    if wiki == "enwiki":
        logger.info("Gathering WP1 ratings...")
        readme_lines.append("ratings.tsv: page_title project quality importance\n")
        logger.info("Gathering importances...")
        with ratings_tsv_fp.open("w", encoding="utf-8") as f:
            write_tsv_rows_to_file(f, _fetch_ratings_from_db(wp10db))

    ######################################################################
    # GATHER VITAL ARTICLES FOR WPEN                                     #
    ######################################################################

    vital_tsv_fp = lang_dir / "vital.tsv"
    if wiki == "enwiki":
        logger.info("Gathering vital articles...")
        readme_lines.append("vital.tsv: level page_title\n")
        with vital_tsv_fp.open("w", encoding="utf-8") as f:
            write_tsv_rows_to_file(f, get_vital_articles())

    ######################################################################
    # MERGE LISTS                                                        #
    ######################################################################
    logger.info("Merging lists...")
    readme_lines.append(
        "all.tsv: page_title page_id page_size langlinks_count "
        "pageviews_count [rating1] [rating2] ...\n"
    )
    all_tsv_fp = lang_dir / "all.tsv"
    with all_tsv_fp.open("w", encoding="utf-8") as f:
        write_tsv_rows_to_file(
            f,
            _merge_rows(
                pages_tsv_fp,
                pageviews_tsv_fp,
                ratings_tsv_fp,
            ),
        )

    ######################################################################
    # COMPUTE SCORES                                                     #
    ######################################################################
    logger.info("Computing scores...")
    readme_lines.append("scores.tsv: page_title score\n")
    scores_tsv_fp = lang_dir / "scores.tsv"
    with scores_tsv_fp.open("w", encoding="utf-8") as f:
        write_tsv_rows_to_file(f, generate_scores(all_tsv_fp))

    ######################################################################
    # COMPUTE TOP SELECTIONS                                             #
    ######################################################################
    logger.info("Creating TOP selections...")
    readme_lines.append("tops/*tsv: page_title (one file per TOP selection)\n")
    build_top_selections(scores_tsv_fp, lang_dir / "tops")

    ######################################################################
    # COMPUTE PROJECT SELECTIONS                                         #
    ######################################################################
    logger.info("Creating wikiproject selections...")
    readme_lines.append("projects/*tsv: page_title (one file per project)\n")
    en_needed_dir = data_dir / "en.needed"
    projects_dir = lang_dir / "projects"
    wiki_langlinks_fp = tmp_dir / f"{lang_code}.langlinks.tsv"
    if wiki == "enwiki":
        build_enwiki_projects_list(projects_dir, scores_tsv_fp, all_tsv_fp)
        shutil.rmtree(en_needed_dir, ignore_errors=True)
        en_needed_dir.mkdir(parents=True)
        shutil.copytree(projects_dir, en_needed_dir / "projects")
        shutil.copy(pages_tsv_fp, en_needed_dir / pages_tsv_fp.name)
    else:
        build_langlinks(lang_code, en_needed_dir, wiki_langlinks_fp)
        shutil.rmtree(projects_dir, ignore_errors=True)
        projects_dir.mkdir(parents=True)

        src_files = sorted(
            project
            for project in (en_needed_dir / "projects").iterdir()
            if project.is_file()
        )
        with ProcessPoolExecutor(max_workers=8) as executor:
            futures = [
                executor.submit(
                    build_translated_list,
                    project,
                    lang_code,
                    scores_tsv_fp,
                    wiki_langlinks_fp,
                    projects_dir,
                )
                for project in src_files
            ]
            for future in as_completed(futures):
                future.result()
    ######################################################################
    # CUSTOM selections                                                  #
    ######################################################################
    logger.info("Creating custom selections...")
    readme_lines.append("customs/*tsv: page_title (one file per custom selection)\n")
    custom_dir = lang_dir / "customs"
    build_custom_selections(lang_code, scores_tsv_fp, data_dir, custom_dir, tmp_dir)
    if wiki == "enwiki":
        shutil.copytree(custom_dir, en_needed_dir / "customs")

    readme_fp.write_text("".join(readme_lines), encoding="utf-8")

    ######################################################################
    # COMPRESS all files                                                 #
    ######################################################################
    logger.info("Compressing all files...")
    _compress_all(lang_dir)

    ######################################################################
    # UPLOAD to wp1.kiwix.org                                            #
    ######################################################################
    _upload_dir(lang_dir)

    ######################################################################
    # CLEAN DIRECTORY                                                    #
    ######################################################################

    logger.info("Remove temporary data")

    shutil.rmtree(lang_dir, ignore_errors=True)
    wiki_langlinks_fp.unlink(missing_ok=True)

    cutoff = time.time() - 60 * 86400
    for entry in tmp_dir.iterdir():
        try:
            old = entry.stat().st_mtime < cutoff
        except FileNotFoundError:
            continue

        if not old:
            continue

        if entry.is_dir():
            shutil.rmtree(entry, ignore_errors=True)
        else:
            entry.unlink(missing_ok=True)

    logger.info(f"Process finished for {wiki}")


def build_all_selections(
    min_article_count: int = 0,
    offset: str | None = None,
    data_dir: pathlib.Path = DATA_DIR,
):
    """Build selections for every Wikipedia above ``min_article_count``."""
    for lang in get_wiki_languages_exceeding_count(min_article_count):
        if offset is not None:
            if lang.code == offset:
                offset = None
            else:
                continue

        for attempt in range(1, 5):
            logger.info("Run %d for %s", attempt, lang)
            try:
                build_selections(lang.code, data_dir)
            except Exception:
                logger.exception("Build failed for %s (run %d)", lang, attempt)
                time.sleep(1)
            else:
                break

    logger.info("All selections have been built successfully")


def main():
    parser = argparse.ArgumentParser(
        description="Build WP1 selection lists for Wikipedia languages."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser(
        "build", help="Build selections for a single language."
    )
    build_parser.add_argument("lang", help="Wikipedia language code (e.g. 'en', 'fr').")
    build_parser.add_argument(
        "--data-dir",
        type=pathlib.Path,
        default=DATA_DIR,
        help="Directory holding cached pagecounts and intermediate data "
        "(default: %(default)s).",
    )

    all_parser = subparsers.add_parser(
        "build-all", help="Build selections for every Wikipedia."
    )
    all_parser.add_argument(
        "--min-articles",
        type=int,
        default=0,
        help="Only build Wikipedias with more than this many pages "
        "(default: %(default)s).",
    )
    all_parser.add_argument(
        "--offset",
        help="Language code to resume from (skips every language before it).",
    )
    all_parser.add_argument(
        "--data-dir",
        type=pathlib.Path,
        default=DATA_DIR,
        help="Directory holding cached pagecounts and intermediate data "
        "(default: %(default)s).",
    )

    list_parser = subparsers.add_parser(
        "list", help="List Wikipedias with more than a given page count."
    )
    list_parser.add_argument(
        "min_articles",
        type=int,
        help="Only list Wikipedias with more than this many pages.",
    )

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    if args.command == "build":
        build_selections(args.lang, args.data_dir)
    elif args.command == "build-all":
        build_all_selections(args.min_articles, args.offset, args.data_dir)
    elif args.command == "list":
        for lang, _, count in get_wiki_languages_exceeding_count(args.min_articles):
            print(f"{lang} {count}")


if __name__ == "__main__":
    main()
