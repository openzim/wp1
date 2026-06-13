import io

from botocore.exceptions import ClientError

import wp1.logic.builder as logic_builder
from wp1.exceptions import (
    ObjectNotFoundError,
    Wp1FatalSelectionError,
    Wp1RetryableSelectionError,
)
from wp1.models.wp10.builder import Builder as Wp10Builder
from wp1.selection.abstract_builder import AbstractBuilder


class MetaBuilder(AbstractBuilder):
    """Base class for builders that reference other builders."""

    META_BUILDER_MODELS = {"wp1.selection.models.combinator"}

    def _builder_model(self, builder: Wp10Builder) -> str:
        return self._as_text(getattr(builder, "b_model", ""))

    def _builder_label(self, builder: Wp10Builder) -> str:
        name = getattr(builder, "b_name", None)
        builder_id = self._as_text(getattr(builder, "b_id", ""))
        if name is not None:
            return f"{self._as_text(name)} ({builder_id})"
        return builder_id

    def _reference_label(self, wp10db, builder_id: str) -> str:
        try:
            builder = logic_builder.get_builder(wp10db, builder_id)
        except ObjectNotFoundError:
            return builder_id
        return self._builder_label(builder)

    def _is_meta_builder(self, builder: Wp10Builder) -> bool:
        return self._builder_model(builder) in self.META_BUILDER_MODELS

    def _dedupe(self, builder_ids: list[str]) -> list[str]:
        seen: set[str] = set()
        unique_ids: list[str] = []
        for builder_id in builder_ids:
            if builder_id not in seen:
                seen.add(builder_id)
                unique_ids.append(builder_id)
        return unique_ids

    def _fetch_selection_data(
        self, wp10db, s3, builder_id: str, reference_label: str | None = None
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

        status = self._as_text(selection.s_status)
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
