import pathlib
import re
import math
from collections.abc import Generator, Iterable
from typing import NamedTuple, cast

from wp1.selection_tools.models import (
    PageLangLinkCount,
    PageLinkCount,
    PageMetrics,
    PageSize,
    Pageview,
    ScoredPage,
    ScoredTitle,
    WikiLang,
    decode_row,
    parse_page_metrics,
)
import csv
from pymysql import Connection
import logging
from bz2 import BZ2Decompressor
from datetime import datetime, timedelta

import requests

from wp1.constants import WP1_USER_AGENT
from wp1.config import get_settings
from wp1.exceptions import Wp1ScoreProcessingError
from wp1.time import get_current_datetime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pymysql.cursors import Cursor
logger = logging.getLogger(__name__)


QUALITY_SCORES = {
    "FA-Class": 500,
    "FL-Class": 500,
    "A-Class": 400,
    "GA-Class": 400,
    "Bplus-Class": 350,
    "B-Class": 300,
    "C-Class": 225,
    "Start-Class": 150,
    "Stub-Class": 50,
}
IMPORTANCE_SCORES = {
    "Top-Class": 400,
    "High-Class": 300,
    "Mid-Class": 200,
    "Low-Class": 100,
}

_RATING_RE = re.compile(r"(.+?)=([^:]+):(.+)")


class Rating(NamedTuple):
    project: str
    quality: str
    importance: str


def _log10(value: float) -> float:
    return math.log10(value) if value else 0.0


def _parse_rating(rating: str) -> Rating:
    m = _RATING_RE.fullmatch(rating)
    if m is None:
        raise ValueError(f"Unable to parse rating {rating!r}")
    return Rating(m.group(1), m.group(2), m.group(3))


def _compute_external_importance(links: float, langlinks: float, views: float) -> int:
    # This is the original WP1 0.7 method (conceived for the WPEN
    # selection). This method has proven to be quite weak in case of
    # $pageLinksCount and $langLinksCount are quite high because of
    # artefacts (lots of detailed articles pointing to a global
    # generic one).
    return int(100 * _log10(views) + 100 * _log10(links) + 100 * _log10(langlinks))


def _compute_internal_quality(ratings: list[str]) -> int:
    total, count = 0, 0
    for rating in ratings:
        quality = _parse_rating(rating).quality
        total += QUALITY_SCORES.get(quality, 0)
        count += 1
    return int(total / count) if total else 0


def _compute_internal_importance(ratings: list[str]) -> int:
    total, count = 0, 0
    for rating in ratings:
        importance = _parse_rating(rating).importance
        total += IMPORTANCE_SCORES.get(importance, 0)
        count += 1
    return int(total / count) if total else 0


def generate_scores_from_rows(
    rows: Iterable[PageMetrics],
) -> Generator[ScoredTitle, None, None]:
    """Compute a score for each set of page metrics."""
    top_ratings: dict[str, dict[str, int]] = {}
    articles: dict[str, dict] = {}

    for row in rows:
        title = row.title
        links = row.links
        langlinks = row.langlinks
        views = row.views
        ratings = [str(rating) for rating in row.ratings]

        # Accumulate Top-Class stats per project
        for rating in ratings:
            project, _, importance = _parse_rating(rating)
            if importance == "Top-Class":
                top_rating = top_ratings.setdefault(
                    project, {"count": 0, "links": 0, "langlinks": 0, "views": 0}
                )
                top_rating["count"] += 1
                top_rating["links"] += links
                top_rating["langlinks"] += langlinks
                top_rating["views"] += views

        articles[title] = {
            "projects": [_parse_rating(rating).project for rating in ratings],
            "quality": _compute_internal_quality(ratings),
            "importance": _compute_internal_importance(ratings),
            "external": _compute_external_importance(links, langlinks, views),
        }

    # Project scores
    for top_rating in top_ratings.values():
        count = top_rating["count"]
        top_rating["score"] = int(
            (
                _compute_external_importance(
                    top_rating["links"] / count,
                    top_rating["langlinks"] / count,
                    top_rating["views"] / count,
                )
                - 1000
            )
            / 2
        )

    results: list[ScoredTitle] = []
    for title, article in articles.items():
        project_score = 0
        for project in article["projects"]:
            score = top_ratings.get(project, {}).get("score", 0)
            if score > project_score:
                project_score = score

        score = (
            article["quality"]
            + article["importance"]
            + project_score
            + article["external"]
        )
        results.append(ScoredTitle(title, score))

    results.sort(key=lambda item: item.score, reverse=True)
    yield from results


def generate_scores(src: pathlib.Path) -> Generator[ScoredTitle, None, None]:
    def rows():
        with src.open(encoding="utf-8") as f:
            for line in f:
                yield parse_page_metrics(line)

    yield from generate_scores_from_rows(rows())


def wiki_languages() -> Generator[WikiLang, None, None]:
    r = requests.get(
        "https://wikistats.wmcloud.org/api.php?action=dump&table=wikipedias&format=csv",
        headers={"User-Agent": WP1_USER_AGENT},
        timeout=60,
    )
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise Wp1ScoreProcessingError("Could not retrieve wiki list") from e

    reader = csv.reader(r.text.splitlines())
    # Skip the header row
    next(reader, None)
    for row in reader:
        yield WikiLang(name=row[1], code=row[2], total=int(row[3]))


def get_wiki_languages_exceeding_count(count: int) -> list[WikiLang]:
    """Get only wikipedia languages whose total exceeds count.

    Entries are sorted by name in descending order
    """
    return sorted(
        (wiki_lang for wiki_lang in wiki_languages() if wiki_lang.total > count),
        key=lambda w: w.name,
        reverse=True,
    )


def get_pageview_url(prev: bool = False) -> str:
    weeks = 4
    if prev:
        weeks = 8

    now = get_current_datetime()
    dt = datetime(now.year, now.month, 1) - timedelta(weeks=weeks)
    return dt.strftime(
        "https://dumps.wikimedia.org/other/pageview_complete/monthly/"
        "%Y/%Y-%m/pageviews-%Y%m-user.bz2"
    )


def get_pageview_file_path(filename: str) -> pathlib.Path:
    path = pathlib.Path(get_settings().FILE_PATH_PAGEVIEWS)
    path.mkdir(exist_ok=True)
    return path / filename


def get_prev_file_path() -> pathlib.Path:
    prev_filename = get_pageview_url(prev=True).split("/")[-1]
    return get_pageview_file_path(prev_filename)


def get_cur_file_path() -> pathlib.Path:
    cur_filename = get_pageview_url().split("/")[-1]
    return get_pageview_file_path(cur_filename)


def download_pageviews() -> None:
    # Clean up file from last month
    prev_filepath = get_prev_file_path()
    if prev_filepath.exists():
        prev_filepath.unlink()

    cur_filepath = get_cur_file_path()
    if cur_filepath.exists():
        # File already downloaded
        logger.info("Pageviews file already downloaded.")
        return

    logger.info(f"Downloading pageviews file to {cur_filepath}")

    with requests.get(get_pageview_url(), stream=True, timeout=60) as r:
        r.raise_for_status()
        try:
            with open(cur_filepath, "wb") as f:
                # Read data in 8 MB chunks
                for chunk in r.iter_content(chunk_size=8 * 1024 * 1024):
                    f.write(chunk)
        except Exception as e:
            logger.exception("Error downloading pageviews")
            cur_filepath.unlink()
            raise Wp1ScoreProcessingError("Error downloading pageviews") from e

    logger.info(f"Downloaded pageviews file to {cur_filepath}")


def raw_pageviews(
    fp: pathlib.Path, decode: bool = False
) -> Generator[str | bytes, None, None]:
    def as_bytes():
        decompressor = BZ2Decompressor()
        trailing = b""
        with open(fp, "rb") as f:
            while True:
                # Read data in 1 MB chunks
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                data = decompressor.decompress(chunk)
                lines = [line for line in data.split(b"\n") if line]
                if not lines:
                    continue

                # Reunite incomplete lines
                yield trailing + lines[0]
                yield from lines[1:-1]
                trailing = lines[-1]

            # Nothing left, yield the last line
            yield trailing

    if decode:
        for line in as_bytes():
            yield line.decode("utf-8")
    else:
        yield from as_bytes()


def pageview_components(fp: pathlib.Path) -> Generator[Pageview, None, None]:
    tally = None
    for line in raw_pageviews(fp):
        line = cast(bytes, line)
        parts = line.split(b" ")
        if len(parts) != 6 or parts[2] == b"null":
            # Skip pages that don't have a pageid
            continue

        if parts[1] == b"" or parts[1] == b"-":
            # Skip pages that don't have a title
            continue

        lang = parts[0].split(b".")[0].decode("utf-8")
        name = parts[1].decode("utf-8")
        page_id = parts[2].decode("utf-8")
        try:
            views = int(parts[4])
        except ValueError:
            logger.warning("Views field wasn't int in pageview dump: %r", line)
            continue

        if (
            tally is not None
            and tally.lang == lang
            and tally.name == name
            and tally.page_id == page_id
        ):
            # This is a view on the same page from a different interface (mobile v
            # desktop etc)
            tally = tally._replace(views=tally.views + views)
        else:
            # Language code, article name, article page id, views
            if tally is not None:
                yield tally
            tally = Pageview(*decode_row((lang, name, page_id, views)))

    if tally is not None:
        yield tally


def reset_missing_articles_pageviews(wp10db: "Connection[Cursor]"):
    with wp10db.cursor() as cursor:
        cursor.execute("""
      UPDATE page_scores
      LEFT JOIN temp_pageviews
      ON page_scores.ps_article = temp_pageviews.tp_article
      SET page_scores.ps_views = 0
      WHERE temp_pageviews.tp_article IS NULL;
      """)
    wp10db.commit()


def insert_temp_pageviews(
    wp10db: "Connection[Cursor]",
    lang: str,
    article: str,
    page_id: int | str,
    views: int,
):
    with wp10db.cursor() as cursor:
        cursor.execute(
            """INSERT INTO temp_pageviews (tp_lang, tp_page_id, tp_article, tp_views)
              VALUES (%(lang)s, %(page_id)s, %(article)s, %(views)s)
              ON DUPLICATE KEY UPDATE tp_views = %(views)s
          """,
            {"lang": lang, "page_id": page_id, "article": article, "views": views},
        )


def insert_temp_redirects(
    wp10db: "Connection[Cursor]",
    lang: str,
    rows: Iterable[tuple[str, str]],
):
    """Stage the redirects as source -> target title pairs.

    Chains are flattened afterwards by resolve_temp_redirects.
    """
    with wp10db.cursor() as cursor:
        cursor.executemany(
            """INSERT INTO temp_redirects (tr_lang, tr_source, tr_target)
              VALUES (%s, %s, %s)
              ON DUPLICATE KEY UPDATE tr_target = VALUES(tr_target)""",
            ((lang, source, target) for source, target in rows),
        )
    wp10db.commit()


def insert_temp_pagesize(
    wp10db: "Connection[Cursor]",
    lang: str,
    rows: Iterable[PageSize],
    commit: bool = True,
):
    """Insert each page's size in temp_pagesize."""
    with wp10db.cursor() as cursor:
        cursor.executemany(
            """INSERT INTO temp_pagesize
                (tp_lang, tp_page_id, tp_article, tp_size)
              VALUES (%s, %s, %s, %s)
              ON DUPLICATE KEY UPDATE
                tp_article = VALUES(tp_article),
                tp_size = VALUES(tp_size)""",
            ((lang, row.page_id, row.article, row.size) for row in rows),
        )
    if commit:
        wp10db.commit()


def insert_temp_pagelinks(
    wp10db: "Connection[Cursor]",
    lang: str,
    rows: Iterable[PageLinkCount],
    commit: bool = True,
):
    """Insert each page's links in temp_pagelinks."""
    with wp10db.cursor() as cursor:
        cursor.executemany(
            """INSERT INTO temp_pagelinks
                (tp_lang, tp_page_id, tp_article, tp_links)
              VALUES (%s, %s, %s, %s)
              ON DUPLICATE KEY UPDATE
                tp_article = VALUES(tp_article),
                tp_links = VALUES(tp_links)""",
            ((lang, row.page_id, row.article, row.links) for row in rows),
        )
    if commit:
        wp10db.commit()


def insert_temp_pagelanglinks(
    wp10db: "Connection[Cursor]",
    lang: str,
    rows: Iterable[PageLangLinkCount],
    commit: bool = True,
):
    """Insert each page's language links in temp_pagelanglinks."""
    with wp10db.cursor() as cursor:
        cursor.executemany(
            """INSERT INTO temp_pagelanglinks
                (tp_lang, tp_page_id, tp_article, tp_lang_links)
              VALUES (%s, %s, %s, %s)
              ON DUPLICATE KEY UPDATE
                tp_article = VALUES(tp_article),
                tp_lang_links = VALUES(tp_lang_links)""",
            ((lang, row.page_id, row.article, row.langlinks) for row in rows),
        )
    if commit:
        wp10db.commit()


def insert_temp_pagescores(
    wp10db: "Connection[Cursor]",
    lang: str,
    rows: Iterable[ScoredPage],
    commit: bool = True,
):
    """Insert each page's score in temp_pagescores."""
    with wp10db.cursor() as cursor:
        cursor.executemany(
            """INSERT INTO temp_pagescores
                (tp_lang, tp_page_id, tp_article, tp_score)
              VALUES (%s, %s, %s, %s)
              ON DUPLICATE KEY UPDATE
                tp_article = VALUES(tp_article),
                tp_score = VALUES(tp_score)""",
            ((lang, row.page_id, row.article, row.score) for row in rows),
        )
    if commit:
        wp10db.commit()


def swap_temp_pageviews_to_scores(wp10db: "Connection[Cursor]"):
    """Copy the staged pageviews into page_scores."""
    statement = """INSERT INTO page_scores
            (ps_lang, ps_page_id, ps_article, ps_views)
        SELECT tp_lang, tp_page_id, tp_article, tp_views
        FROM temp_pageviews
        ON DUPLICATE KEY UPDATE
            ps_article = VALUES(ps_article),
            ps_views = VALUES(ps_views);"""
    with wp10db.cursor() as cursor:
        cursor.execute(statement)
        wp10db.commit()


def resolve_temp_redirects(wp10db: "Connection[Cursor]"):
    """Follow redirect-to-redirect chains so each source maps to its target."""
    with wp10db.cursor() as cursor:
        while True:
            cursor.execute("""UPDATE temp_redirects r
                JOIN temp_redirects n
                    ON n.tr_lang = r.tr_lang AND n.tr_source = r.tr_target
                SET r.tr_target = n.tr_target
                WHERE r.tr_target <> n.tr_target""")
            if cursor.rowcount == 0:
                break
    wp10db.commit()


def fold_redirect_metrics(wp10db: "Connection[Cursor]"):
    """Add each redirect page's staged metrics to the page it points at."""
    folds = (
        ("temp_pagelinks", "tp_links"),
        ("temp_pagelanglinks", "tp_lang_links"),
        ("temp_pageviews", "tp_views"),
    )
    with wp10db.cursor() as cursor:
        for table, column in folds:
            cursor.execute(f"""UPDATE {table} tgt
                JOIN temp_redirects r
                    ON r.tr_lang = tgt.tp_lang AND r.tr_target = tgt.tp_article
                JOIN {table} src
                    ON src.tp_lang = r.tr_lang AND src.tp_article = r.tr_source
                SET tgt.{column} = tgt.{column} + src.{column}""")
            cursor.execute(f"""DELETE src FROM {table} src
                JOIN temp_redirects r
                    ON r.tr_lang = src.tp_lang AND r.tr_source = src.tp_article""")
        cursor.execute("""DELETE p FROM temp_pagesize p
            JOIN temp_redirects r
                ON r.tr_lang = p.tp_lang AND r.tr_source = p.tp_article""")
    wp10db.commit()


def swap_temp_pagesize_to_scores(wp10db: "Connection[Cursor]"):
    """Copy the staged page sizes into page_scores."""
    statement = """INSERT INTO page_scores
            (ps_lang, ps_page_id, ps_article, ps_size)
        SELECT tp_lang, tp_page_id, tp_article, tp_size
        FROM temp_pagesize
        ON DUPLICATE KEY UPDATE
            ps_article = VALUES(ps_article),
            ps_size = VALUES(ps_size);"""
    with wp10db.cursor() as cursor:
        cursor.execute(statement)
        wp10db.commit()


def swap_temp_pagelinks_to_scores(wp10db: "Connection[Cursor]"):
    """Copy the staged page links into page_scores."""
    statement = """INSERT INTO page_scores
            (ps_lang, ps_page_id, ps_article, ps_links)
        SELECT tp_lang, tp_page_id, tp_article, tp_links
        FROM temp_pagelinks
        ON DUPLICATE KEY UPDATE
            ps_article = VALUES(ps_article),
            ps_links = VALUES(ps_links);"""
    with wp10db.cursor() as cursor:
        cursor.execute(statement)
        wp10db.commit()


def swap_temp_pagelanglinks_to_scores(wp10db: "Connection[Cursor]"):
    """Copy the staged language links into page_scores."""
    statement = """INSERT INTO page_scores
            (ps_lang, ps_page_id, ps_article, ps_lang_links)
        SELECT tp_lang, tp_page_id, tp_article, tp_lang_links
        FROM temp_pagelanglinks
        ON DUPLICATE KEY UPDATE
            ps_article = VALUES(ps_article),
            ps_lang_links = VALUES(ps_lang_links);"""
    with wp10db.cursor() as cursor:
        cursor.execute(statement)
        wp10db.commit()


def swap_temp_pagescores_to_scores(wp10db: "Connection[Cursor]"):
    """Copy the staged scores into page_scores."""
    statement = """INSERT INTO page_scores
            (ps_lang, ps_page_id, ps_article, ps_score)
        SELECT tp_lang, tp_page_id, tp_article, tp_score
        FROM temp_pagescores
        ON DUPLICATE KEY UPDATE
            ps_article = VALUES(ps_article),
            ps_score = VALUES(ps_score);"""
    with wp10db.cursor() as cursor:
        cursor.execute(statement)
        wp10db.commit()


def truncate_temp_pageviews(wp10db: "Connection[Cursor]"):
    with wp10db.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE temp_pageviews;")
    wp10db.commit()


def truncate_temp_redirects(wp10db: "Connection[Cursor]"):
    with wp10db.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE temp_redirects;")
    wp10db.commit()


def truncate_temp_pagesize(wp10db: "Connection[Cursor]"):
    with wp10db.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE temp_pagesize;")
    wp10db.commit()


def truncate_temp_pagelinks(wp10db: "Connection[Cursor]"):
    with wp10db.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE temp_pagelinks;")
    wp10db.commit()


def truncate_temp_pagelanglinks(wp10db: "Connection[Cursor]"):
    with wp10db.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE temp_pagelanglinks;")
    wp10db.commit()


def truncate_temp_pagescores(wp10db: "Connection[Cursor]"):
    with wp10db.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE temp_pagescores;")
    wp10db.commit()


def finalize_page_scores(wp10db: "Connection[Cursor]"):
    """Run the delayed final update of page_scores from the temp tables."""
    logger.debug("Swapping data from the temp tables to the page_scores table")
    swap_temp_pageviews_to_scores(wp10db)
    swap_temp_pagesize_to_scores(wp10db)
    swap_temp_pagelinks_to_scores(wp10db)
    swap_temp_pagelanglinks_to_scores(wp10db)
    swap_temp_pagescores_to_scores(wp10db)
    reset_missing_articles_pageviews(wp10db)
    truncate_temp_pageviews(wp10db)
    truncate_temp_pagesize(wp10db)
    truncate_temp_pagelinks(wp10db)
    truncate_temp_pagelanglinks(wp10db)
    truncate_temp_pagescores(wp10db)
    logger.info("Transaction Done")


def load_temp_pageviews(
    wp10db: "Connection[Cursor]",
    filter_lang: str | None = None,
    commit_after: int = 50000,
):
    """Download the pageview dump and stage the views in temp_pageviews"""
    download_pageviews()

    if filter_lang is None:
        logger.info("Updating all pageviews")
    else:
        logger.info("Updating pageviews for %s", filter_lang)

    try:
        truncate_temp_pageviews(wp10db)
        n = 0
        current_lang = None
        for lang, article, page_id, views in pageview_components(get_cur_file_path()):
            if filter_lang is None or lang == filter_lang:
                insert_temp_pageviews(wp10db, lang, article, page_id, views)
                n += 1
            else:
                if lang != current_lang:
                    current_lang = lang
                    logger.debug(f"Skpping insert for lang {current_lang}")

            if n >= commit_after:
                logger.debug("Committing in temp db")
                wp10db.commit()
                n = 0
        wp10db.commit()
    except Exception as e:
        wp10db.rollback()
        truncate_temp_pageviews(wp10db)
        logger.error("Transaction failed: %s", e)
