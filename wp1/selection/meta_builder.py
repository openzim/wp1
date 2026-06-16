import io

from botocore.exceptions import ClientError

import wp1.logic.builder as logic_builder
from wp1.logic import util as logic_util
from wp1.exceptions import (
    Wp1FatalSelectionError,
    Wp1RetryableSelectionError,
)
from wp1.selection.abstract_builder import AbstractBuilder


class MetaBuilder(AbstractBuilder):
    """Base class for builders that reference other builders."""

    def _fetch_selection_data(
        self, wp10db, s3, builder_id: str, reference_label: str | None = None
    ) -> bytes:
        """Fetch the latest materialized TSV snapshot for a referenced builder."""
        label = reference_label or builder_id
        selection = logic_builder.latest_selection_for(
            wp10db, builder_id, "text/tab-separated-values"
        )

        # TODO: #1196 - Add retry handling for Combinator referenced selections.
        if selection is None:
            raise Wp1RetryableSelectionError(
                f"Referenced builder {label} has no usable selection "
                f"(no selection found)"
            )

        status = logic_util.as_text(selection.s_status)
        if status == "FAILED":
            raise Wp1FatalSelectionError(
                f"Referenced builder {label} latest selection failed"
            )

        if status != "OK":
            raise Wp1RetryableSelectionError(
                f"Referenced builder {label} latest selection is not ready "
                f"(status={status!r})"
            )

        # OK selections can have no stored data when materialization produced empty
        # data, since AbstractBuilder only uploads filled selection.data.
        if selection.s_object_key is None:
            raise Wp1RetryableSelectionError(
                f"Referenced builder {label} latest selection has no stored data"
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
