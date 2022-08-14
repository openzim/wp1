import io
import json
import logging

from wp1.constants import CONTENT_TYPE_TO_EXT
import wp1.logic.builder as logic_builder
import wp1.logic.selection as logic_selection
from wp1.models.wp10.selection import Selection

logger = logging.getLogger(__name__)


class AbstractBuilder:

  def _upload_to_storage(self, s3, selection, builder):
    object_key = logic_selection.object_key_for_selection(
        selection, builder.b_model.decode('utf-8'))

    upload_data = io.BytesIO()
    upload_data.write(selection.data)
    upload_data.seek(0)
    logger.info('Uploading to path: %s ' % object_key)
    s3.upload_fileobj(upload_data, key=object_key)

  def materialize(self, s3, wp10db, builder, content_type):
    params = json.loads(builder.b_params)
    next_version = logic_selection.get_next_version(wp10db, builder.b_id,
                                                    content_type)

    selection = Selection(s_content_type=content_type.encode('utf-8'),
                          s_builder_id=builder.b_id,
                          s_version=next_version)
    selection.set_id()
    selection.data = self.build(content_type, **params)
    selection.set_updated_at_now()
    self._upload_to_storage(s3, selection, builder)

    logger.info('Saving selection %s to database' %
                selection.s_id.decode('utf-8'))
    logic_selection.insert_selection(wp10db, selection)
    logic_builder.update_current_version(wp10db, builder, next_version)

  def build(self, content_type, **params):
    raise NotImplementedError()

  def validate(self, **params):
    raise NotImplementedError()
