from typing import TYPE_CHECKING, Any
import time
from collections.abc import Generator
from wp1 import app_logging
import subprocess
from concurrent.futures import as_completed
from concurrent.futures.process import ProcessPoolExecutor
import shutil
from pymysql import Connection
from wp1.selection_tools.scores import (
    finalize_page_scores,
    fold_redirect_metrics,
    generate_scores_from_rows,
    get_wiki_languages_exceeding_count,
    insert_temp_pagelanglinks,
    insert_temp_pagelinks,
    insert_temp_pagescores,
    insert_temp_pagesize,
    insert_temp_redirects,
    load_temp_pageviews,
    resolve_temp_redirects,
    truncate_temp_pagesize,
    truncate_temp_redirects,
)
from wp1.selection_tools.constants import BASE_DIR, DATA_DIR
from wp1.selection_tools.custom import build_custom_selections
from wp1.selection_tools.models import (
    LangLink,
    Page,
    PageLangLinkCount,
    PageLink,
    PageLinkCount,
    PageMetrics,
    PageScore,
    PageScoreWithRatings,
    PageSize,
    PageTitleCount,
    ScoredPage,
    ArticleRating,
    Redirect,
    decode_row,
)
from wp1.selection_tools.projects_list import build_translated_list
import pathlib
from wp1.selection_tools.projects_list import build_langlinks
from wp1.wp10_db import connect as wp10_connect
from wp1.selection_tools import write_tsv_rows_to_file
from wp1.selection_tools.wiki.en import (
    build_projects_list as build_enwiki_projects_list,
    get_vital_articles,
)
from wp1 import wikilang_db
import argparse
import logging

if TYPE_CHECKING:
    from pymysql.cursors import Cursor

from typing import NamedTuple

from wp1.time import get_current_datetime

logger = logging.getLogger(__name__)


def fetch_paginated_rows_from_db(
    conn: "Connection[Cursor]", statement: str, batch_size: int, row_type: type
) -> Generator[Any, None, None]:
    """Fetch rows from a range query, stopping when a batch is empty."""
    lower = 0
    with conn.cursor() as cursor:
        while True:
            upper = lower + batch_size
            cursor.execute(statement, (lower, upper))
            rows = cursor.fetchall()
            if not rows:
                break
            for row in rows:
                yield row_type(*decode_row(row))
            lower = upper


def fetch_ratings_from_db(
    wp10db: "Connection[Cursor]",
) -> Generator[ArticleRating, None, None]:
    "Fetch ratings data from teh ratings table"
    stmt = """
    SELECT r_article, r_project, r_quality, r_importance
    FROM ratings
    """
    with wp10db.cursor() as cursor:
        cursor.execute(
            "SELECT DISTINCT r_importance FROM ratings where r_importance IS NOT NULL"
        )
        importances = [importance for (importance,) in cursor.fetchall()]
        for importance in importances:
            logger.info(f"Gathering ratings with importance {importance}...")
            cursor.execute(stmt + " WHERE r_importance = %s", (importance,))
            while True:
                rows = cursor.fetchmany(10_000)
                if not rows:
                    break
                for row in rows:
                    yield ArticleRating(*decode_row(row))

        logger.info("Gathering ratings with importance IS NULL...")
        cursor.execute(stmt + " WHERE r_importance IS NULL")
        while True:
            rows = cursor.fetchmany(10_000)
            if not rows:
                break
            for row in rows:
                yield ArticleRating(*decode_row(row))


def fetch_pageviews_from_db(
    wp10db: "Connection[Cursor]", lang_code: str
) -> Generator[PageTitleCount, None, None]:
    """Fetch pages and view data from the temp_pageviews table"""
    stmt = """
    SELECT tp_article, tp_views
    FROM temp_pageviews
    WHERE tp_lang = %s AND tp_views > 0
    ORDER BY tp_article
    """
    with wp10db.cursor() as cursor:
        cursor.execute(stmt, (lang_code,))
        while True:
            rows = cursor.fetchmany(10_000)
            if not rows:
                break
            for row in rows:
                yield PageTitleCount(*decode_row(row))


def fetch_page_scores_from_db(
    wp10db: "Connection[Cursor]", lang_code: str
) -> Generator[PageScore, None, None]:
    """Fetch scores data from thte page_scores table"""
    stmt = """
    SELECT ps_page_id, ps_article, ps_links, ps_lang_links, ps_views, ps_score
    FROM page_scores
    WHERE ps_lang = %s
    ORDER BY ps_score DESC
    """
    with wp10db.cursor() as cursor:
        cursor.execute(stmt, (lang_code,))
        while True:
            rows = cursor.fetchmany(10_000)
            if not rows:
                break
            for row in rows:
                yield PageScore(*decode_row(row))


def fetch_langlinks_from_db(
    wikidb: "Connection[Cursor]",
) -> Generator[LangLink, None, None]:
    stmt = """
    SELECT page_title, ll_lang, ll_title
    FROM langlinks, page
    WHERE langlinks.ll_from = page.page_id AND page.page_namespace = 0
    """
    with wikidb.cursor() as cursor:
        cursor.execute(stmt)
        while True:
            rows = cursor.fetchmany(10_000)
            if not rows:
                break
            for row in rows:
                # Replace spaces with underscores
                columns = (col.replace(" ", "_") for col in decode_row(row))
                yield LangLink(*columns)


def fetch_redirects_from_db(
    wikidb: "Connection[Cursor]",
) -> Generator[Redirect, None, None]:
    stmt = """
    SELECT page.page_title, redirect.rd_title
    FROM redirect
    JOIN page ON page.page_id = redirect.rd_from
    WHERE redirect.rd_namespace = 0 AND page.page_namespace = 0
    """
    with wikidb.cursor() as cursor:
        cursor.execute(stmt)
        while True:
            rows = cursor.fetchmany(10_000)
            if not rows:
                break
            for row in rows:
                yield Redirect(*decode_row(row))


def fetch_pagesize_from_db(
    wp10db: "Connection[Cursor]", lang_code: str
) -> Generator[Page, None, None]:
    """Fetch page size data from temp_pagesize table"""
    stmt = """
    SELECT tp_page_id, tp_article, tp_size
    FROM temp_pagesize
    WHERE tp_lang = %s
    ORDER BY tp_page_id
    """
    with wp10db.cursor() as cursor:
        cursor.execute(stmt, (lang_code,))
        while True:
            rows = cursor.fetchmany(10_000)
            if not rows:
                break
            for row in rows:
                yield Page(*decode_row(row))


def fetch_page_metrics_from_db(
    wp10db: "Connection[Cursor]", lang_code: str, with_ratings: bool
) -> Generator[PageMetrics, None, None]:
    """Read each page's staged metrics back for scoring.

    Joins the per-metric temp tables (and, for enwiki, the project ratings)
    into a single metric row per page. The temp tables are 1:1 on the page, so
    only the ratings need aggregating.
    """
    ratings_select = (
        "GROUP_CONCAT(CONCAT(r.r_project, '=', r.r_quality, ':', r.r_importance))"
        if with_ratings
        else "NULL"
    )
    ratings_join = (
        "LEFT JOIN ratings r ON r.r_article = p.tp_article" if with_ratings else ""
    )
    stmt = f"""
    SELECT p.tp_page_id, p.tp_article, p.tp_size,
           COALESCE(pl.tp_links, 0) AS links,
           COALESCE(ll.tp_lang_links, 0) AS langlinks,
           COALESCE(tpv.tp_views, 0) AS views,
           {ratings_select} AS ratings
    FROM temp_pagesize p
    LEFT JOIN temp_pagelinks pl
        ON pl.tp_lang = p.tp_lang AND pl.tp_article = p.tp_article
    LEFT JOIN temp_pagelanglinks ll
        ON ll.tp_lang = p.tp_lang AND ll.tp_article = p.tp_article
    LEFT JOIN temp_pageviews tpv
        ON tpv.tp_lang = p.tp_lang AND tpv.tp_article = p.tp_article
    {ratings_join}
    WHERE p.tp_lang = %s
    GROUP BY p.tp_page_id, p.tp_article, p.tp_size,
             pl.tp_links, ll.tp_lang_links, tpv.tp_views
    """
    with wp10db.cursor() as cursor:
        cursor.execute(stmt, (lang_code,))
        while True:
            rows = cursor.fetchmany(10_000)
            if not rows:
                break
            for row in rows:
                page_id, article, size, links, langlinks, views, ratings = decode_row(
                    row
                )
                rating_list = tuple(ratings.split(",")) if ratings else ()
                yield PageMetrics(
                    article, page_id, size, links, langlinks, views, rating_list
                )


def fetch_page_scores_and_ratings_from_db(
    wp10db: "Connection[Cursor]",
    lang_code: str,
) -> Generator[PageScoreWithRatings, None, None]:
    """Fetch page scores with ratings from database"""
    stmt = """
    SELECT ps_article, ps_page_id, ps_size, ps_links, ps_lang_links, ps_views,
           GROUP_CONCAT(CONCAT(r_project, '=', r_quality, ':', r_importance)) as ratings_str
    FROM page_scores
    JOIN ratings ON ps_article = r_article
    WHERE ps_lang = %s
    GROUP BY ps_page_id, ps_article, ps_size, ps_links, ps_lang_links, ps_views
    ORDER BY ps_score DESC
    """
    with wp10db.cursor() as cursor:
        cursor.execute(stmt, (lang_code,))
        while True:
            rows_batch = cursor.fetchmany(10_000)
            if not rows_batch:
                break
            for row in rows_batch:
                fields = decode_row(row)
                article, page_id, size, links, langlinks, views, ratings = fields
                rating_list = tuple(ratings.split(",")) if ratings else ()
                yield PageScoreWithRatings(
                    article, page_id, size, links, langlinks, views, rating_list
                )


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
    """Compress fp with 7-Zip and remove the original."""
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
    logger.info(f"Creating directrories for storing artifacts at {data_dir}...")
    tmp_dir = data_dir / "tmp"
    lang_dir = tmp_dir / (wiki + "_" + get_current_datetime().strftime("%Y-%m"))
    tmp_dir.mkdir(parents=True, exist_ok=True)
    lang_dir.mkdir(parents=True, exist_ok=True)
    readme_fp = lang_dir / "README"
    readme_lines: list[str] = []

    ######################################################################
    # GATHER PAGES KEYS VALUES                                           #
    ######################################################################

    ## Page views
    ## Download page views into the temp_pageviews table
    logger.info("Gathering pageviews....")
    load_temp_pageviews(wp10db, lang_code)
    readme_lines.append("pageviews.tsv: page_title view_count\n")
    logger.info("Writing pageviews.tsv")
    pageviews_tsv_fp = lang_dir / "pageviews.tsv"
    with pageviews_tsv_fp.open("w", encoding="utf-8") as f:
        write_tsv_rows_to_file(f, fetch_pageviews_from_db(wp10db, lang_code))

    ## Gather redirects so their links, language links and views can be folded
    ## onto the pages they point at.
    logger.info("Gathering redirects...")
    truncate_temp_redirects(wp10db)
    insert_temp_redirects(wp10db, lang_code, fetch_redirects_from_db(wikidb))
    resolve_temp_redirects(wp10db)

    ## Pages
    logger.info("Gathering pages...")
    readme_lines.append("pages.tsv: page_id page_title page_size\n")
    pages_tsv_fp = lang_dir / "pages.tsv"
    pages_sql = """
    SELECT page.page_id, page.page_title, revision.rev_len
    FROM page
    JOIN revision ON revision.rev_id = page.page_latest
    WHERE page.page_namespace = 0
     AND page.page_id >= %s AND page.page_id < %s
    ORDER BY page.page_id
    """
    # Maps an article title to its page id so that links, language links and
    # scores can be attributed to the page they belong to.
    page_ids: dict[str, int] = {}

    def _page_size_rows(page_ids: dict[str, int]) -> Generator[PageSize, None, None]:
        for page in fetch_paginated_rows_from_db(wikidb, pages_sql, 100_000, Page):
            page_ids[page.title] = page.page_id
            yield PageSize(page.page_id, page.title, page.size)

    truncate_temp_pagesize(wp10db)
    insert_temp_pagesize(wp10db, lang_code, _page_size_rows(page_ids))

    ## Page links
    logger.info("Gathering page links...")
    pagelinks_sql = """
    SELECT pl_from, lt_title AS pl_title
    FROM pagelinks
    LEFT JOIN linktarget ON pl_target_id = lt_id
    WHERE lt_namespace = 0  AND pl_from_namespace = 0
        AND pl_from >= %s AND pl_from < %s
    """
    link_counts: dict[str, int] = {}
    for link in fetch_paginated_rows_from_db(wikidb, pagelinks_sql, 10_000, PageLink):
        if link.target in page_ids:
            link_counts[link.target] = link_counts.get(link.target, 0) + 1

    insert_temp_pagelinks(
        wp10db,
        lang_code,
        (
            PageLinkCount(page_id, title, link_counts.get(title, 0))
            for title, page_id in page_ids.items()
        ),
    )
    del link_counts

    ## Language links
    logger.info("Gathering language links...")
    langlink_counts: dict[str, int] = {}
    for langlink in fetch_langlinks_from_db(wikidb):
        title = langlink.source_title
        if title in page_ids:
            langlink_counts[title] = langlink_counts.get(title, 0) + 1

    insert_temp_pagelanglinks(
        wp10db,
        lang_code,
        (
            PageLangLinkCount(page_id, title, langlink_counts.get(title, 0))
            for title, page_id in page_ids.items()
        ),
    )
    del langlink_counts

    ## Fold the metrics of redirect pages into their targets.
    logger.info("Folding redirect metrics...")
    fold_redirect_metrics(wp10db)

    ## Pages
    logger.info("Writing pages.tsv...")
    with pages_tsv_fp.open("w", encoding="utf-8") as f:
        write_tsv_rows_to_file(f, fetch_pagesize_from_db(wp10db, lang_code))

    ######################################################################
    # GATHER WP1 RATINGS FOR WPEN                                        #
    ######################################################################

    ratings_tsv_fp = lang_dir / "ratings.tsv"
    if wiki == "enwiki":
        logger.info("Gathering WP1 ratings...")
        readme_lines.append("ratings.tsv: page_title project quality importance\n")
        with ratings_tsv_fp.open("w", encoding="utf-8") as f:
            write_tsv_rows_to_file(f, fetch_ratings_from_db(wp10db))

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
    # SCORE AND RUN THE FINAL UPDATE                                     #
    ######################################################################
    logger.info("Scoring pages...")
    scores_by_title = dict(
        generate_scores_from_rows(
            fetch_page_metrics_from_db(wp10db, lang_code, with_ratings=wiki == "enwiki")
        )
    )
    insert_temp_pagescores(
        wp10db,
        lang_code,
        (
            ScoredPage(page_ids[title], title, score)
            for title, score in scores_by_title.items()
        ),
    )

    del page_ids, scores_by_title

    finalize_page_scores(wp10db)

    ######################################################################
    # COMPUTE SCORES                                                     #
    ######################################################################
    logger.info("Computing scores...")
    scores_tsv_fp = lang_dir / "scores.tsv"
    readme_lines.append("scores.tsv: page_title score\n")
    scores_tsv_fp = lang_dir / "scores.tsv"

    with scores_tsv_fp.open("w", encoding="utf-8") as f:
        write_tsv_rows_to_file(
            f,
            (
                (row.article, row.score)
                for row in fetch_page_scores_from_db(wp10db, lang_code)
            ),
        )

    logger.info("Merging lists...")
    readme_lines.append(
        "all.tsv: page_title page_id page_size pagelinks_count langlinks_count "
        "pageviews_count [rating1] [rating2] ...\n"
    )
    all_tsv_fp = lang_dir / "all.tsv"
    with all_tsv_fp.open("w", encoding="utf-8") as f:
        write_tsv_rows_to_file(
            f,
            (
                row.as_tsv_row()
                for row in fetch_page_scores_and_ratings_from_db(wp10db, lang_code)
            ),
        )

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
        if (en_needed_dir / "projects").exists():
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

    wp10db.close()
    wikidb.close()

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

    if args.command == "build":
        build_selections(args.lang, args.data_dir)
    elif args.command == "build-all":
        build_all_selections(args.min_articles, args.offset, args.data_dir)
    elif args.command == "list":
        for lang, _, count in get_wiki_languages_exceeding_count(args.min_articles):
            print(f"{lang} {count}")


if __name__ == "__main__":
    app_logging.configure_logging()
    main()
