from typing import Any

from pymysql.connections import Connection

import wp1.logic.project as logic_project
import wp1.logic.rating as logic_rating
from wp1.exceptions import Wp1FatalSelectionError
from wp1.selection.abstract_builder import AbstractBuilder


def _encode(value: str | None) -> bytes | None:
    return value.encode("utf-8") if value else None


def _project_name(wikiproject: str) -> bytes:
    return wikiproject.strip().replace(" ", "_").encode("utf-8")


class Builder(AbstractBuilder):
    """Articles of one WikiProject, filtered like the project's article table."""

    def build(self, content_type: str, **params: Any) -> bytes:
        if content_type != "text/tab-separated-values":
            raise Wp1FatalSelectionError("Unrecognized content type")
        if "wp10db" not in params:
            raise Wp1FatalSelectionError("Missing param `wp10db`")
        if not params.get("wikiproject"):
            raise Wp1FatalSelectionError("Missing param `wikiproject`")

        ratings = logic_rating.iterate_project_rating_by_type(
            params["wp10db"],
            _project_name(params["wikiproject"]),
            quality=_encode(params.get("quality")),
            importance=_encode(params.get("importance")),
            pattern=params.get("pattern") or None,
        )
        return "\n".join(
            rating.r_article.decode("utf-8")
            for rating in ratings
            if rating.r_namespace == 0
        ).encode("utf-8")

    def validate(
        self, **params: Any
    ) -> tuple[list[str] | str, list[str] | str, list[str]]:
        if "wp10db" not in params:
            raise Wp1FatalSelectionError("Cannot validate without param `wp10db`")
        wikiproject = params.get("wikiproject")
        if not wikiproject:
            return ([], [], ["Missing WikiProject"])

        wp10db: Connection = params["wp10db"]
        if logic_project.get_project_by_name(wp10db, _project_name(wikiproject)):
            return ([wikiproject], [], [])
        return ([], [wikiproject], ["The WikiProject does not exist"])
