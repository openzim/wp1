import io
import json
import logging
from typing import Any

from kiwixstorage import KiwixStorage
from pymysql.connections import Connection

import wp1.logic.builder as logic_builder
import wp1.logic.selection as logic_selection
from wp1.constants import CONTENT_TYPE_TO_EXT
from wp1.exceptions import (
    Wp1FatalSelectionError,
    Wp1RetryableSelectionError,
    Wp1SelectionError,
)
from wp1.models.wp10.builder import Builder
from wp1.models.wp10.selection import Selection

logger = logging.getLogger(__name__)


class AbstractBuilder:

    def _as_text(self, value: bytes | str | int | None) -> str:
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return str(value)

    def _upload_to_storage(
        self, s3: KiwixStorage, selection: Selection, builder: Builder
    ) -> None:
        object_key = logic_selection.object_key_for_selection(
            selection,
            builder.b_model.decode("utf-8"),
            name=builder.b_name.decode("utf-8"),
        )

        if selection.data is None:
            raise ValueError("Cannot upload selection with no data")
        upload_data = io.BytesIO()
        upload_data.write(selection.data)
        upload_data.seek(0)
        logger.info("Uploading to path: %s " % object_key)
        s3.upload_fileobj(upload_data, key=object_key)
        selection.s_object_key = object_key

    def materialize(
        self,
        s3: KiwixStorage,
        wp10db: Connection,
        builder: Builder,
        content_type: str,
        version: int,
    ) -> None:
        params = json.loads(builder.b_params)

        if builder.b_id is None:
            raise ValueError("Cannot materialize builder without b_id")

        selection = Selection(
            s_content_type=content_type.encode("utf-8"),
            s_builder_id=builder.b_id,
            s_version=version,
            s_status=b"OK",
        )
        selection.set_id()
        try:
            selection.data = self.build(
                content_type,
                project=builder.b_project.decode("utf-8"),
                wp10db=wp10db,
                s3=s3,
                **params,
            )
            selection.s_article_count = selection.data.count(b"\n") + 1
        except Wp1RetryableSelectionError as e:
            logger.exception("Error materializing builder id=%s", builder.b_id)
            selection.s_status = "CAN_RETRY"
            logic_selection.set_error_messages(selection, e)
        except (Wp1FatalSelectionError, Wp1SelectionError) as e:
            logger.exception("Error materializing builder id=%s", builder.b_id)
            selection.s_status = "FAILED"
            logic_selection.set_error_messages(selection, e)

        selection.set_updated_at_now()
        # Data might be None if build operation didn't succeed.
        if selection.data:
            self._upload_to_storage(s3, selection, builder)

        if selection.s_id is None:
            raise ValueError("Selection has no s_id after set_id()")
        logger.info("Saving selection %s to database", selection.s_id.decode("utf-8"))
        logic_selection.insert_selection(wp10db, selection)

    def build(self, content_type: str, **params: Any) -> bytes:
        raise NotImplementedError()

    def validate(
        self, **params: Any
    ) -> tuple[list[str] | str, list[str] | str, list[str]]:
        raise NotImplementedError()
