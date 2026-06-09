import io
import logging
from typing import Any

from botocore.exceptions import ClientError

import wp1.logic.builder as logic_builder
from wp1.exceptions import (
    ObjectNotFoundError,
    Wp1FatalSelectionError,
    Wp1RetryableSelectionError,
)
from wp1.models.wp10.builder import Builder as Wp10Builder
from wp1.selection.abstract_builder import AbstractBuilder

logger = logging.getLogger(__name__)


META_BUILDER_MODELS = {"wp1.selection.models.combinator"}


# TODO: #1181 - Move shared helpers into AbstractBuilder.
def _as_text(value: bytes | str | int | None) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return str(value)


def _builder_label(builder: Wp10Builder) -> str:
    name = getattr(builder, "b_name", None)
    builder_id = _as_text(getattr(builder, "b_id", ""))
    if name is not None:
        return f"{_as_text(name)} ({builder_id})"
    return builder_id


def _reference_label(wp10db, builder_id: str) -> str:
    try:
        builder = logic_builder.get_builder(wp10db, builder_id)
    except ObjectNotFoundError:
        return builder_id
    return _builder_label(builder)


def _builder_model(builder: Wp10Builder) -> str:
    return _as_text(getattr(builder, "b_model", ""))


def _is_meta_builder(builder: Wp10Builder) -> bool:
    return _builder_model(builder) in META_BUILDER_MODELS


def _dedupe(builder_ids: list[str]) -> list[str]:
    seen: set[str] = set()
    unique_ids: list[str] = []
    for builder_id in builder_ids:
        if builder_id not in seen:
            seen.add(builder_id)
            unique_ids.append(builder_id)
    return unique_ids


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


# TODO: #1181 - Move shared title parsing helpers into AbstractBuilder.
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


# TODO: #1181 - Move shared set operation helpers into AbstractBuilder.
def _apply_operation(operation: str, sets: list[set[str]]) -> set[str]:
    if not sets:
        return set()

    if operation == "union":
        return set.union(*sets)

    if operation == "intersection":
        return set.intersection(*sets)

    raise ValueError(f"Unsupported operation: {operation}")


def _fetch_selection_data(
    wp10db, s3, builder_id: str, reference_label: str | None = None
) -> bytes:
    """Fetch the latest materialized TSV snapshot for a referenced builder."""
    label = reference_label or builder_id
    selection = logic_builder.latest_selection_for(
        wp10db, builder_id, "text/tab-separated-values"
    )

    if selection is None:
        raise Wp1RetryableSelectionError(
            f"Referenced builder {label} has no usable selection "
            f"(no selection found)"
        )

    status = _as_text(selection.s_status)
    if status == "FAILED":
        raise Wp1FatalSelectionError(
            f"Referenced builder {label} latest selection failed"
        )

    if status != "OK":
        raise Wp1RetryableSelectionError(
            f"Referenced builder {label} latest selection is not ready "
            f"(status={status!r})"
        )

    # OK selections can have no object key when materialization produced empty
    # data, since AbstractBuilder only uploads filled selection.data.
    if selection.s_object_key is None:
        raise Wp1RetryableSelectionError(
            f"Referenced builder {label} latest selection has no object key"
        )

    object_key = selection.s_object_key
    if isinstance(object_key, bytes):
        object_key = object_key.decode("utf-8")

    buffer = io.BytesIO()
    try:
        s3.download_fileobj(object_key, buffer)
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "Unknown")
        raise Wp1RetryableSelectionError(
            f"Failed to download selection for builder {label} "
            f"from S3 key {object_key!r}: {code}"
        ) from e

    return buffer.getvalue()


def _process_group(wp10db, s3, group: dict[str, Any]) -> set[str]:

    builder_values = group.get("builders", [])

    builder_ids = [
        builder_id for builder_id in builder_values if isinstance(builder_id, str)
    ]

    operation = group.get("operation", "union")

    sets: list[set[str]] = []
    # TODO: #1184 - Handle multiple bad referenced selections in combinator build.
    for builder_id in _dedupe(builder_ids):
        data = _fetch_selection_data(
            wp10db, s3, builder_id, _reference_label(wp10db, builder_id)
        )
        title_set = _parse_tsv_to_set(data)
        sets.append(title_set)

    return _apply_operation(operation, sets)


class Builder(AbstractBuilder):
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

        referenced_ids = _dedupe(include_builders + exclude_builders)

        if builder_id is not None and _as_text(builder_id) in referenced_ids:
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

            # name + id is only for helping testing, in prod we dont show the id
            # TODO : show the name only
            label = _builder_label(builder)

            if _as_text(builder.b_user_id) != _as_text(user_id):
                errors.append(
                    f"Builder {label} belongs to another user. You can only "
                    "reference your own builders."
                )
            if _as_text(builder.b_project) != _as_text(project):
                errors.append(
                    f"Builder {label} belongs to project "
                    f"{_as_text(builder.b_project)!r}. All referenced builders "
                    "must use the same project."
                )
            if _is_meta_builder(builder):
                errors.append(
                    f"Builder {label} is a combinator. Combinators can only "
                    "reference leaf builders such as Simple, SPARQL, PetScan, "
                    "Book, or WikiProject."
                )

        if errors:
            return ([], [], errors)

        return ([], [], [])

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

        include_set = _process_group(wp10db, s3, include_group)

        exclude_set: set[str] = set()
        if exclude_group is not None:
            exclude_builders = exclude_group.get("builders", [])
            if exclude_builders:
                exclude_set = _process_group(wp10db, s3, exclude_group)

        result = include_set - exclude_set

        if not result:
            raise Wp1FatalSelectionError("Combinator produced no articles")

        return "\n".join(sorted(result)).encode("utf-8")
