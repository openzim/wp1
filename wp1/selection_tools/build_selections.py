from collections import defaultdict
from concurrent.futures import as_completed
from concurrent.futures.process import ProcessPoolExecutor
import shutil
from pymysql import Connection
from wp1.selection_tools.projects_list import build_translated_list
import pathlib
from wp1.selection_tools.projects_list import build_langlinks
from wp1.selection_tools.scores import generate_scores
from wp1.wp10_db import connect as wp10_connect
from wp1.selection_tools import write_tsv_rows_to_file
from wp1.selection_tools.wiki.en import (
    build_projects_list as build_enwiki_projects_list,
)
from typing import Iterable
import bz2
import tempfile
from pymysql.cursors import Cursor
import requests
import re
from lxml import html
import xml.etree.ElementTree as ET
from wp1 import wikilang_db
from wp1.constants import WP1_USER_AGENT
from wp1.selection_tools.wiki.en import get_vital_articles
from wp1.exceptions import Wp1ScoreProcessingError
import logging

from typing import NamedTuple

from wp1.time import get_current_datetime

logger = logging.getLogger(__name__)

CHUNK_SIZE = 8 * 1024 * 1024  # chunk size for downloads


class PageCountEntry(NamedTuple):
    link: str
    filename: str
    size: int | None  # in bytes


def get_wikipedia_namespaces(lang_code: str) -> list[str]:
    """
    Get the sorted set of namespaces for Wikipedia using its ISO639-1 language code
    """

    url = (
        f"https://{lang_code}.wikipedia.org/w/api.php?"
        "action=query&meta=siteinfo&siprop=namespaces&formatversion=2"
        "&format=xml"
    )

    r = requests.get(
        url=url,
        headers={"User-Agent": WP1_USER_AGENT},
        timeout=60,
    )
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise Wp1ScoreProcessingError(
            f"Could not retrieve namespace info for {lang_code}"
        ) from e

    namespaces: set[str] = set()
    root = ET.fromstring(r.content)
    for ns in root.findall(".//ns"):
        canonical = ns.get("canonical")
        if canonical:
            namespaces.add(canonical)

        ns_id = ns.get("id")
        if ns_id:
            ns_name = ns.text
            if ns_name:
                namespaces.add(ns_name)
    # Replace all spaces with underscore and sort
    return sorted({name.replace(" ", "_") for name in namespaces})


def get_pagecounts(start: int = 2017) -> list[PageCountEntry]:
    """Get the pagecount links from Wikimedia dumps from start year."""

    base_url = "https://dumps.wikimedia.org/other/pagecounts-ez/merged/"

    r = requests.get(
        url=base_url,
        headers={"User-Agent": WP1_USER_AGENT},
        timeout=60,
    )
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise Wp1ScoreProcessingError(
            "Could not retrieve pagecount links from wikimedia dumps"
        ) from e

    results: list[PageCountEntry] = []
    root = html.fromstring(r.content)

    for link in root.xpath('//a[contains(@href, "totals.bz")]'):
        filename = link.get("href")
        match = re.search(r"pagecounts-(\d{4})-", filename)
        if not match or int(match.group(1)) < start:
            logger.debug(
                f"Filename {filename} does not match pagecounts regex. Skipping..."
            )
            continue

        # Try to parse the size information from the text node. It is usually the last
        # text in the HTML after the date
        size = None
        if link.tail:
            size = int(link.tail.strip().split(" ")[-1])
        else:
            logger.warning(f"Couldn't fetch size information for file {filename}")

        results.append(
            PageCountEntry(link=base_url + filename, filename=filename, size=size)
        )
    return results


def get_new_pagecount_entries(
    data_dir: pathlib.Path, updates: list[PageCountEntry]
) -> list[PageCountEntry]:
    """
    Determine which page count entries are new based on updates.

    An update in udpates is considered new if:
    - it does not exist in data_dir
    - it does not have a size information
    - its size is different from a file with the same name in data_dir
    """
    results: list[PageCountEntry] = []
    for update in updates:
        # Consider entries with no size as new. This should never happen though unless
        # layout of page to retrieve page count entries was updated
        if not update.size:
            results.append(update)
            continue

        local_copy = data_dir / update.filename
        if not local_copy.exists():
            logger.debug(
                f"First time seeting pagecount {update.filename}. Adding to new entries"
            )
            results.append(update)
        else:
            local_size = local_copy.stat().st_size
            if local_size != update.size:
                logger.debug(
                    f"Pagecount {update.filename} size has changed from "
                    f"{local_size} to {update.size} bytes"
                )
                results.append(update)

    return results


def download_pagecount_entry(
    data_dir: pathlib.Path, entry: PageCountEntry
) -> pathlib.Path:
    """Download a pagecount entry to data_dir using its link"""

    data_dir.mkdir(parents=True, exist_ok=True)
    dest_file = data_dir / entry.filename

    with tempfile.NamedTemporaryFile(
        dir=data_dir, delete=False, suffix=".tmp"
    ) as tmp_file:
        tmp_path = pathlib.Path(tmp_file.name)
        try:
            with requests.get(entry.link, stream=True) as response:
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        tmp_file.write(chunk)
            tmp_file.flush()
            tmp_file.close()

            tmp_path.replace(dest_file)
        except Exception:
            tmp_file.close()
            if tmp_path.exists():
                tmp_path.unlink()
            raise
    return dest_file


def process_pagecount_data(
    page_count_fp: pathlib.Path, lang_code: str, namespaces: Iterable[str]
) -> dict[str, int]:
    """Parse the page count file and process data in it"""
    project_prefix = f"{lang_code}.z"
    logger.debug(f"Parsing {page_count_fp}...")

    results: defaultdict[str, int] = defaultdict(int)
    with bz2.open(page_count_fp, "rt", encoding="utf-8") as f:
        for line in f:
            if not line.startswith(project_prefix):
                logger.debug(
                    f"line '{line}' does not start with project prefix "
                    f"{project_prefix}. Skipping..."
                )
                continue

            parts = line.split(" ")
            if len(parts) < 3:
                logger.warning(
                    f"line '{line}' in pagecount ({page_count_fp}) is not up to three "
                    "parts and cannot be processed. Skipping..."
                )
                continue

            title = parts[1]
            try:
                count = int(parts[2])
            except ValueError:
                logger.error(
                    f"second part in line '{line}' is not a valid number. Skipping..."
                )
                continue
            if title.split(":", 1)[0] in namespaces:
                logger.debug(f"line '{line}' contains namespaced title. Skipping...")
                continue
            results[title] += count
    return results


def save_pagecount_results(
    results_fp: pathlib.Path, *pagecount_results: dict[str, int]
) -> dict[str, int]:
    """Save pagecount results file.

    Final results are computed by adding the count of each title across all the pagecounts
    """
    results: defaultdict[str, int] = defaultdict(int)
    # Build up the existing results if the file already exists
    if results_fp.exists():
        with results_fp.open() as f:
            for line in f:
                title, count = line.rstrip("\n").split("\t")
                results[title] = int(count)

    for pagecount_result in pagecount_results:
        for title, count in pagecount_result.items():
            results[title] += count

    with results_fp.open("w") as f:
        for title in sorted(results):
            f.write(f"{title}\t{results[title]}\n")
    return results


def _fetch_paginated_rows_from_db(
    conn: Connection[Cursor], statement: str, batch_size: int
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


def _fetch_ratings_from_db(conn: Connection[Cursor]):
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
            cursor.execute(stmt + " WHERE importance = %s", (importance,))
            while True:
                rows = cursor.fetchmany(10_000)
                if not rows:
                    break
                yield from rows

        logger.info("Gathering ratings with importance IS NULL...")
        cursor.execute(stmt + "WHERE importance IS NULL")
        while True:
            rows = cursor.fetchmany(10_000)
            if not rows:
                break
            yield from rows


def _fetch_redirects_from_db(conn: Connection[Cursor]):
    stmt = """
    SELECT rd_from, rd_title FROM redirect WHERE rd_namespace = 0
    """
    with conn.cursor() as cursor:
        cursor.execute(stmt)
        while True:
            rows = cursor.fetchmany(10_000)
            if not rows:
                break
            yield from rows


def _fetch_langlinks_from_db(conn: Connection[Cursor]):
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
    pagelinks_fp: pathlib.Path,
    langlinks_fp: pathlib.Path,
    pageviews_fp: pathlib.Path,
    redirects_fp: pathlib.Path,
    ratings_fp: pathlib.Path,
):
    """Merge the generated TSV files and write to dest"""
    counts = defaultdict(dict)
    id_to_title: dict[int, str] = {}

    with pages_fp.open() as f:
        for line in f:
            page_id, title, size, is_redirect = line.rstrip("\n").split("\t")
            page_id = int(page_id)
            is_redirect = int(is_redirect)

            counts[title]["i"] = page_id
            if not is_redirect:
                counts[title]["s"] = int(size)
            id_to_title[page_id] = title

    with pagelinks_fp.open() as f:
        for line in f:
            _, target = line.rstrip("\n").split("\t", 1)
            counts[target]["l"] = counts[target].get("l", -1) + 1

    with langlinks_fp.open() as f:
        for line in f:
            title = line.split("\t", 1)[0]
            if title:
                counts[title]["ll"] = counts[title].get("ll", -1) + 1

    with pageviews_fp.open() as f:
        for line in f:
            title, views = line.rstrip("\n").split("\t")
            counts[title]["v"] = int(views)

    with redirects_fp.open() as f:
        for line in f:
            source_id, target = line.rstrip("\n").split("\t")
            source_id = int(source_id)
            source_title = id_to_title[source_id]
            if not source_id or source_title not in counts:
                continue
            if target in counts:
                for key in ("l", "ll", "v"):
                    src_val = counts[source_title].get(key)
                    if src_val:
                        counts[target][key] = counts[target].get(key, 0) + src_val

            del counts[source_title]
            del id_to_title[source_id]

    if ratings_fp.exists():
        with ratings_fp.open() as f:
            for line in f:
                title, project, quality, importance = line.rstrip("\n").split("\t")
                counts[title].setdefault("r", []).append(
                    f"{project}={quality}:{importance}"
                )

    with pages_fp.open() as f:
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
    with scores_fp.open() as f:
        for line in f:
            if total < max_top:
                titles.append(line.split("\t", 1)[0])
            total += 1

    for top in tops:
        if total > top:
            (tops_dir / f"{top}.tsv").write_text("\n".join(titles[:top]) + "\n")
        else:
            break


def build_selections(lang_code: str, start: int, data_dir: pathlib.Path):
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

    namespaces = get_wikipedia_namespaces(lang_code)
    pagecounts = get_pagecounts(start)

    new_page_counts = get_new_pagecount_entries(data_dir, pagecounts)
    new_page_count_fps: list[pathlib.Path] = []

    for page_count in new_page_counts:
        logger.info(f"Downloading page count data from {page_count.link}")
        new_page_count_fps.append(download_pagecount_entry(data_dir, page_count))

    page_count_results: list[dict[str, int]] = []
    for new_page_count_fp in new_page_count_fps:
        logger.info(f"Parsing {new_page_count_fp}...")
        page_count_results.append(
            process_pagecount_data(new_page_count_fp, lang_code, namespaces)
        )

    ######################################################################
    # GATHER PAGES KEYS VALUES                                           #
    ######################################################################

    ## Pages
    readme_fp.write_text("pageviews.tsv: page_title view_count\n")
    pageviews_tsv_fp = lang_dir / "pageviews.tsv"
    save_pagecount_results(pageviews_tsv_fp, *page_count_results)
    # Free up the memory used by the page count results as this could get very big
    page_count_results = []

    logger.info("Gathering pages...")
    readme_fp.write_text("pages.tsv: page_id page_title page_size is_redirect\n")

    pages_tsv_fp = lang_dir / "pages.tsv"
    pages_sql = """
    SELECT page.page_id, page.page_title, revision.rev_len, page.page_is_redirect
    FROM page
    JOIN revision ON revision.rev_id = page.page_latest
    WHERE page.page_namespace = 0
      AND page.page_id >= %s AND page.page_id < %s
    """
    with pages_tsv_fp.open("w") as f:
        write_tsv_rows_to_file(
            f, _fetch_paginated_rows_from_db(wikidb, pages_sql, 100_0000)
        )

    ## Page links
    logger.info("Gatering page links...")
    readme_fp.write_text("pagelinks.tsv: source_page_id target_page_title\n")
    pagelinks_tsv_fp = lang_dir / "pagelinks.tsv"
    pagelinks_sql = """
    SELECT pl_from, lt_title AS pl_title 
    FROM pagelinks 
    LEFT JOIN linktarget ON pl_target_id = lt_id 
    WHERE lt_namespace = 0  AND pl_from_namespace = 0 
        AND pl_from >= %s AND pl_from < %s
    """
    with pagelinks_tsv_fp.open("w") as f:
        write_tsv_rows_to_file(
            f, _fetch_paginated_rows_from_db(wikidb, pagelinks_sql, 10_000)
        )

    ## Language links
    logger.info("Gathering language links...")
    readme_fp.write_text(
        "langlinks.tsv: source_page_title language_code target_page_title\n"
    )
    langlinks_tsv_fp = lang_dir / "langlinks.tsv"
    with langlinks_tsv_fp.open("w") as f:
        write_tsv_rows_to_file(f, _fetch_langlinks_from_db(wikidb))

    ## Redirects
    logger.info("Gathering redirects...")
    readme_fp.write_text("redirects.tsv: source_page_id target_page_title\n")
    redirects_tsv_fp = lang_dir / "redirects.tsv"
    with redirects_tsv_fp.open("w") as f:
        write_tsv_rows_to_file(f, _fetch_redirects_from_db(wikidb))

    ######################################################################
    # GATHER WP1 RATINGS FOR WPEN                                        #
    ######################################################################

    ratings_tsv_fp = lang_dir / "ratings.tsv"
    if wiki == "enwiki":
        logger.info("Gathering WP1 ratings...")
        readme_fp.write_text("ratings.tsv: page_title project quality importance\n")
        logger.info("Gathering importances...")
        with ratings_tsv_fp.open("w") as f:
            write_tsv_rows_to_file(f, _fetch_ratings_from_db(wp10db))

    ######################################################################
    # GATHER VITAL ARTICLES FOR WPEN                                     #
    ######################################################################

    vital_tsv_fp = lang_dir / "vital.tsv"
    if wiki == "enwiki":
        logger.info("Gathering vital articles...")
        readme_fp.write_text("vital.tsv: level page_title\n")
        with vital_tsv_fp.open("w") as f:
            write_tsv_rows_to_file(f, get_vital_articles())

    ######################################################################
    # MERGE LISTS                                                        #
    ######################################################################
    logger.info("Merging lists...")
    readme_fp.write_text(
        "all.tsv: page_title page_id page_size pagelinks_count langlinks_count "
        "pageviews_count [rating1] [rating2] ...\n"
    )
    all_tsv_fp = lang_dir / "all.tsv"
    with all_tsv_fp.open("w") as f:
        write_tsv_rows_to_file(
            f,
            _merge_rows(
                pages_tsv_fp,
                pagelinks_tsv_fp,
                langlinks_tsv_fp,
                pageviews_tsv_fp,
                redirects_tsv_fp,
                ratings_tsv_fp,
            ),
        )

    ######################################################################
    # COMPUTE SCORES                                                     #
    ######################################################################
    logger.info("Computing scores...")
    readme_fp.write_text("scores.tsv: page_title score\n")
    scores_tsv_fp = lang_dir / "scores.tsv"
    with scores_tsv_fp.open("w") as f:
        write_tsv_rows_to_file(f, generate_scores(all_tsv_fp))

    ######################################################################
    # COMPUTE TOP SELECTIONS                                             #
    ######################################################################
    logger.info("Creating TOP selections...")
    readme_fp.write_text("tops/*tsv: page_title (one file per TOP selection)\n")
    build_top_selections(scores_tsv_fp, lang_dir / "tops")

    ######################################################################
    # COMPUTE PROJECT SELECTIONS                                         #
    ######################################################################
    logger.info("Creating wikiproject selections...")
    readme_fp.write_text("projects/*tsv: page_title (one file per project)\n")
    en_needed_dir = data_dir / "en.needed"
    projects_dir = lang_dir / "projects"
    wiki_langlinks_fp = tmp_dir / f"{lang_code}.langlinks.tsv"
    if wiki == "enwiki":
        build_enwiki_projects_list(projects_dir, scores_tsv_fp, all_tsv_fp)
        shutil.rmtree(en_needed_dir, ignore_errors=True)
        en_needed_dir.mkdir(parents=True)
        shutil.copytree(projects_dir, en_needed_dir / "projects")
        shutil.copy(pages_tsv_fp, en_needed_dir / pages_tsv_fp.name)
        shutil.copy(langlinks_tsv_fp, en_needed_dir / langlinks_tsv_fp.name)
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
