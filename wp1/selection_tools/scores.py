import pathlib
import re
import math
from collections.abc import Generator
from typing import NamedTuple


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
        _, quality, _ = _parse_rating(rating)
        total += QUALITY_SCORES.get(quality, 0)
        count += 1
    return int(total / count) if total else 0


def _compute_internal_importance(ratings: list[str]) -> int:
    total, count = 0, 0
    for r in ratings:
        _, _, importance = _parse_rating(r)
        total += IMPORTANCE_SCORES.get(importance, 0)
        count += 1
    return int(total / count) if total else 0


def generate_scores(src: pathlib.Path) -> Generator[tuple[str, int], None, None]:
    top_ratings: dict[str, dict[str, int]] = {}
    articles: dict[str, dict] = {}

    with src.open() as f:
        for line in f:
            fields = line.rstrip("\n").split("\t")
            title = fields[0]
            links = int(fields[3])
            langlinks = int(fields[4])
            views = int(fields[5])
            ratings = fields[6:]

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
                "projects": [_parse_rating(rating)[0] for rating in ratings],
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

    results: list[tuple[str, int]] = []
    for title, article in articles.items():
        project_score = 0
        for project in article["projects"]:
            score = top_ratings.get("project", {}).get("score", 0)
            if score > project_score:
                project_score = score

        score = (
            article["quality"]
            + article["importance"]
            + project_score
            + article["external"]
        )
        results.append(score)

    results.sort(key=lambda item: item[1], reverse=True)
    yield from results
