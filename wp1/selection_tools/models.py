from collections.abc import Mapping
from typing import Any, NamedTuple


def decode_row(row: tuple | Mapping) -> tuple:
    """Decode bytes columns in a database row into strings."""
    values = row.values() if isinstance(row, Mapping) else row
    return tuple(_decode(value) for value in values)


def _decode(value: Any) -> Any:
    if isinstance(value, (bytes, bytearray)):
        return bytes(value).decode("utf-8")
    return value


class Pageview(NamedTuple):
    lang: str
    name: str
    page_id: str | int
    views: int


class WikiLang(NamedTuple):
    name: str
    code: str  # ISO639-1 code for language
    total: int  # total number of articles


class Page(NamedTuple):
    """A page and the length of its latest revision"""

    page_id: int
    title: str
    size: int


class PageLink(NamedTuple):
    """A link from a page to another page's title"""

    source_id: int
    target: str


class PageTitleCount(NamedTuple):
    """A page title and its view count"""

    article: str
    views: int


class LangLink(NamedTuple):
    """A page and its counterpart in another language"""

    source_title: str
    lang: str
    target_title: str


class Redirect(NamedTuple):
    """A redirecting page and the title it points to"""

    source_title: str
    target_title: str


class ArticleRating(NamedTuple):
    """A project's rating of an article"""

    article: str
    project: str
    quality: str
    importance: str


class VitalArticle(NamedTuple):
    """A vital article and its level"""

    level: int
    title: str


class PageScore(NamedTuple):
    """A scored article."""

    page_id: int
    article: str
    links: int
    langlinks: int
    views: int
    score: int


class ScoredTitle(NamedTuple):
    """An article title and its score."""

    title: str
    score: int


class PageSize(NamedTuple):
    """A page and its size, as staged in temp_pagesize."""

    page_id: int
    article: str
    size: int


class PageLinkCount(NamedTuple):
    """A page and how many links point to it, as staged in temp_pagelinks."""

    page_id: int
    article: str
    links: int


class PageLangLinkCount(NamedTuple):
    """A page and how many language links it has, staged in temp_pagelanglinks."""

    page_id: int
    article: str
    langlinks: int


class ScoredPage(NamedTuple):
    """A page and its score, as staged in temp_pagescores."""

    page_id: int
    article: str
    score: int


class PageMetrics(NamedTuple):
    """A page with all of its gathered metrics."""

    title: str
    page_id: int
    size: int
    links: int
    langlinks: int
    views: int
    ratings: tuple[str, ...]
    score: int = 0

    def as_tsv_row(self) -> tuple:
        return (*self[:6], *self.ratings)


class PageScoreWithRatings(NamedTuple):
    """A scored article with its project ratings."""

    article: str
    page_id: int
    size: int
    links: int
    langlinks: int
    views: int
    ratings: tuple[str, ...]

    def as_tsv_row(self) -> tuple:
        return (*self[:6], *self.ratings)


def parse_page_metrics(line: str) -> PageMetrics:
    """Parse a tsv line with no scores into a PageMetrics"""
    fields = line.rstrip("\n").split("\t")
    title, page_id, size, links, langlinks, views, *ratings = fields
    return PageMetrics(
        title,
        int(page_id),
        int(size),
        int(links),
        int(langlinks),
        int(views),
        tuple(ratings),
    )


def parse_page_score_with_ratings(line: str) -> PageScoreWithRatings:
    """Parse a tsv line into PageScoreWithRatings."""
    fields = line.rstrip("\n").split("\t")
    article, page_id, size, links, langlinks, views, *ratings = fields
    return PageScoreWithRatings(
        article,
        int(page_id),
        int(size),
        int(links),
        int(langlinks),
        int(views),
        tuple(ratings),
    )
