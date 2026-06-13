import logging
from typing import Any

import wp1.logic.builder as logic_builder
from wp1.exceptions import (
    ObjectNotFoundError,
    Wp1FatalSelectionError,
)
from wp1.selection.meta_builder import MetaBuilder

logger = logging.getLogger(__name__)


def _validate_group_shape(
    name: str, group: Any, required: bool
) -> tuple[list[str], list[str]]:
    errors: list[str] = []

    if group is None:
        if required:
            errors.append(f"Please add at least one builder to the {name} group")
        return [], errors

    if not isinstance(group, dict):
        return [], [f"The {name} group must be a dictionary"]

    builder_values = group.get("builders", [])
    if builder_values is None:
        builder_values = []
    if not isinstance(builder_values, list):
        return [], [f"The {name} group builder list must be a list"]

    if required and not builder_values:
        errors.append(f"Please add at least one builder to the {name} group")

    builders: list[str] = []
    has_invalid_builder_id = False
    for builder_id in builder_values:
        if not isinstance(builder_id, str) or not builder_id:
            has_invalid_builder_id = True
            continue
        builders.append(builder_id)
    if has_invalid_builder_id:
        errors.append(f"The {name} group contains an invalid builder ID")

    operation = group.get("operation")
    if builder_values and operation not in ("union", "intersection"):
        errors.append(
            f"Please select a valid operation (union or intersection) for the {name} group"
        )

    return builders, errors


def _normalize(line: bytes) -> str | None:
    s = line.decode("utf-8", errors="replace").strip()
    if not s or s.startswith("#"):
        return None
    return s.replace(" ", "_")


def _parse_tsv_to_set(data: bytes) -> set[str]:
    titles: set[str] = set()
    for line in data.split(b"\n"):
        normalized = _normalize(line)
        if normalized is not None:
            titles.add(normalized)
    return titles


def _apply_operation(operation: str, sets: list[set[str]]) -> set[str]:
    if not sets:
        return set()

    if operation == "union":
        return set.union(*sets)

    if operation == "intersection":
        return set.intersection(*sets)

    raise ValueError(f"Unsupported operation: {operation}")


class Builder(MetaBuilder):
    """Combinator builder: combines other builders using set operations."""

    def validate(
        self, **params: Any
    ) -> tuple[list[str] | str, list[str] | str, list[str]]:
        errors: list[str] = []

        include = params.get("include")
        exclude = params.get("exclude")

        include_builders, group_errors = _validate_group_shape("Include", include, True)
        errors.extend(group_errors)
        exclude_builders, group_errors = _validate_group_shape(
            "Exclude", exclude, False
        )
        errors.extend(group_errors)

        if errors:
            return ([], [], errors)

        missing_params = []
        if params.get("wp10db") is None:
            missing_params.append("wp10db")
        if params.get("user_id") is None:
            missing_params.append("user_id")
        if params.get("project") is None:
            missing_params.append("project")
        if missing_params:
            return (
                [],
                [],
                [
                    "Missing required validation parameters: "
                    + ", ".join(missing_params)
                ],
            )

        wp10db = params["wp10db"]
        user_id = params["user_id"]
        project = params["project"]
        builder_id = params.get("builder_id")

        referenced_ids = self._dedupe(include_builders + exclude_builders)

        if builder_id is not None and self._as_text(builder_id) in referenced_ids:
            errors.append("This combinator cannot reference itself")

        if errors:
            return ([], [], errors)

        for reference_id in referenced_ids:
            try:
                builder = logic_builder.get_builder(wp10db, reference_id)
            except ObjectNotFoundError:
                # TODO: #1178 - Think more about broken referenced builders.
                errors.append(
                    f"Builder {reference_id!r} no longer exists. Please remove it "
                    "from this combinator."
                )
                continue

            label = self._builder_label(builder)

            if self._as_text(builder.b_user_id) != self._as_text(user_id):
                errors.append(
                    f"Builder {label} belongs to another user. You can only "
                    "reference your own builders."
                )
            if self._as_text(builder.b_project) != self._as_text(project):
                errors.append(
                    f"Builder {label} belongs to project "
                    f"{self._as_text(builder.b_project)!r}. All referenced builders "
                    "must use the same project."
                )
            if self._is_meta_builder(builder):
                errors.append(
                    f"Builder {label} is a combinator. Combinators can only "
                    "reference leaf builders such as Simple, SPARQL, PetScan, "
                    "Book, or WikiProject."
                )

        if errors:
            return ([], [], errors)

        return ([], [], [])

    def _process_group(self, wp10db, s3, group: dict[str, Any]) -> set[str]:

        builder_values = group.get("builders", [])

        builder_ids = [
            builder_id for builder_id in builder_values if isinstance(builder_id, str)
        ]

        operation = group.get("operation", "union")

        sets: list[set[str]] = []
        # TODO: #1184 - Handle multiple bad referenced selections in combinator build.
        for builder_id in self._dedupe(builder_ids):
            data = self._fetch_selection_data(
                wp10db, s3, builder_id, self._reference_label(wp10db, builder_id)
            )
            title_set = _parse_tsv_to_set(data)
            sets.append(title_set)

        return _apply_operation(operation, sets)

    def build(self, content_type: str, **params: Any) -> bytes:
        """Build the combinator selection from referenced builders."""
        if content_type != "text/tab-separated-values":
            raise Wp1FatalSelectionError(f"Unrecognized content type: {content_type!r}")

        wp10db = params.get("wp10db")
        if wp10db is None:
            raise Wp1FatalSelectionError("Combinator build requires 'wp10db' parameter")

        s3 = params.get("s3")
        if s3 is None:
            raise Wp1FatalSelectionError("Combinator build requires 's3' parameter")

        include_group = params.get("include")
        if include_group is None:
            raise Wp1FatalSelectionError("Missing required 'include' group")

        exclude_group = params.get("exclude")

        include_set = self._process_group(wp10db, s3, include_group)

        exclude_set: set[str] = set()
        if exclude_group is not None:
            exclude_builders = exclude_group.get("builders", [])
            if exclude_builders:
                exclude_set = self._process_group(wp10db, s3, exclude_group)

        result = include_set - exclude_set

        if not result:
            raise Wp1FatalSelectionError("Combinator produced no articles")

        return "\n".join(sorted(result)).encode("utf-8")
