import io

from botocore.exceptions import ClientError

import wp1.logic.builder as logic_builder
from wp1.logic import util as logic_util
from wp1.exceptions import (
    Wp1FatalMetaSelectionError,
    Wp1RetryableMetaSelectionError,
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
            raise Wp1RetryableMetaSelectionError(
                f"Referenced builder {label} has no usable selection "
                f"(no selection found)",
                code="REFERENCED_SELECTION_MISSING",
                reason="has no usable TSV selection yet",
                action="Open this list and create or retry its selection, then retry this Combinator.",
            )

        status = logic_util.as_text(selection.s_status)
        if status == "FAILED":
            raise Wp1FatalMetaSelectionError(
                f"Referenced builder {label} latest selection failed",
                code="REFERENCED_SELECTION_FAILED",
                reason="latest selection failed",
                action="Open this list, fix the failed selection, then update this Combinator.",
            )

        if status != "OK":
            if status == "CAN_RETRY":
                code = "REFERENCED_SELECTION_RETRYABLE_FAILURE"
                reason = "latest selection failed but can be retried"
                action = "Open this list and retry it, then retry this Combinator."
            else:
                code = "REFERENCED_SELECTION_NOT_READY"
                reason = "latest selection is not ready yet"
                action = "Wait for this list to finish processing, then retry this Combinator."

            raise Wp1RetryableMetaSelectionError(
                f"Referenced builder {label} {reason}",
                code=code,
                reason=reason,
                action=action,
            )

        # OK selections can have no stored data when materialization produced empty
        # data, since AbstractBuilder only uploads filled selection.data.
        if selection.s_object_key is None:
            raise Wp1RetryableMetaSelectionError(
                f"Referenced builder {label} latest selection has no stored data",
                code="REFERENCED_SELECTION_NO_DATA",
                reason="latest selection has no stored data",
                action="Retry this list, then retry this Combinator.",
            )

        object_key = selection.s_object_key
        if isinstance(object_key, bytes):
            object_key = object_key.decode("utf-8")

        buffer = io.BytesIO()
        try:
            s3.download_fileobj(object_key, buffer)
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code", "Unknown")
            raise Wp1RetryableMetaSelectionError(
                f"Failed to download selection for referenced builder {label}: {code}",
                code="REFERENCED_SELECTION_DOWNLOAD_FAILED",
                reason="could not download the latest selection",
                action="Retry this Combinator. If it fails again, update the referenced list to recreate its download.",
                object_key=object_key,
                storage_error_code=code,
            ) from e

        return buffer.getvalue()
