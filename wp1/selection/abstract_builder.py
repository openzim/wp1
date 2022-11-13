import io
import json
import logging

from wp1.constants import CONTENT_TYPE_TO_EXT
from wp1.exceptions import Wp1RetryableSelectionError, Wp1FatalSelectionError
import wp1.logic.builder as logic_builder
import wp1.logic.selection as logic_selection
from wp1.models.wp10.selection import Selection

logger = logging.getLogger(__name__)


class AbstractBuilder:

  def _upload_to_storage(self, s3, selection, builder):
    object_key = logic_selection.object_key_for_selection(
        selection,
        builder.b_model.decode('utf-8'),
        name=builder.b_name.decode('utf-8'))

    upload_data = io.BytesIO()
    upload_data.write(selection.data)
    upload_data.seek(0)
    logger.info('Uploading to path: %s ' % object_key)
    s3.upload_fileobj(upload_data, key=object_key)
    selection.s_object_key = object_key

  def materialize(self, s3, wp10db, builder, content_type):
    params = json.loads(builder.b_params)
    next_version = logic_selection.get_next_version(wp10db, builder.b_id,
                                                    content_type)

    selection = Selection(s_content_type=content_type.encode('utf-8'),
                          s_builder_id=builder.b_id,
                          s_version=next_version)
    selection.set_id()
    try:
      selection.data = self.build(content_type,
                                  project=builder.b_project.decode('utf-8'),
                                  **params)
    except Wp1RetryableSelectionError as e:
      selection.s_status = 'CAN_RETRY'
      logic_selection.set_error_messages(selection, e)
    except Wp1FatalSelectionError as e:
      selection.s_status = 'FAILED'
      logic_selection.set_error_messages(selection, e)

    selection.set_updated_at_now()
    # Data might be None if build operation didn't succeed.
    if selection.data:
      self._upload_to_storage(s3, selection, builder)

    logger.info('Saving selection %s to database' %
                selection.s_id.decode('utf-8'))
    logic_selection.insert_selection(wp10db, selection)
    logic_builder.update_current_version(wp10db, builder, next_version)

  def build(self, content_type, **params):
    raise NotImplementedError()

  def validate(self, **params):
    raise NotImplementedError()
