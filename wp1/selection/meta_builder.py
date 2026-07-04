import io

from botocore.exceptions import ClientError

import wp1.logic.builder as logic_builder
from wp1.logic import util as logic_util
from wp1.exceptions import (
    Wp1FatalSelectionError,
    Wp1RetryableSelectionError,
)
from wp1.selection.abstract_builder import AbstractBuilder


# Most dependdency errors only need code/reason/action, details are optional debug fields
def _dependency_error_extra(
    code: str, reason: str, action: str, **details: str
) -> dict[str, str]:
    extra = {
        "dependency_code": code,
        "dependency_reason": reason,
        "dependency_action": action,
    }
    extra.update({key: value for key, value in details.items() if value is not None})
    return extra


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
                f"(no selection found)",
                extra=_dependency_error_extra(
                    "REFERENCED_SELECTION_MISSING",
                    "has no usable TSV selection yet",
                    "Open this list and create or retry its selection, then retry this Combinator.",
                ),
            )

        status = logic_util.as_text(selection.s_status)
        if status == "FAILED":
            raise Wp1FatalSelectionError(
                f"Referenced builder {label} latest selection failed",
                extra=_dependency_error_extra(
                    "REFERENCED_SELECTION_FAILED",
                    "latest selection failed",
                    "Open this list, fix the failed selection, then update this Combinator.",
                ),
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

            raise Wp1RetryableSelectionError(
                f"Referenced builder {label} {reason}",
                extra=_dependency_error_extra(code, reason, action),
            )

        # OK selections can have no stored data when materialization produced empty
        # data, since AbstractBuilder only uploads filled selection.data.
        if selection.s_object_key is None:
            raise Wp1RetryableSelectionError(
                f"Referenced builder {label} latest selection has no stored data",
                extra=_dependency_error_extra(
                    "REFERENCED_SELECTION_NO_DATA",
                    "latest selection has no stored data",
                    "Retry this list, then retry this Combinator.",
                ),
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
                f"Failed to download selection for referenced builder {label}: {code}",
                extra=_dependency_error_extra(
                    "REFERENCED_SELECTION_DOWNLOAD_FAILED",
                    "could not download the latest selection",
                    "Retry this Combinator. If it fails again, update the referenced list to recreate its download.",
                    object_key=object_key,
                    storage_error_code=code,
                ),
            ) from e

        return buffer.getvalue()
