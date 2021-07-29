import io
import json

from wp1.constants import CONTENT_TYPE_TO_EXT
import wp1.logic.selection as logic_selection
from wp1.models.wp10.selection import Selection


class AbstractBuilder:

  def _upload_to_storage(self, s3, selection, builder):
    ext = CONTENT_TYPE_TO_EXT.get(selection.s_content_type, '').encode('utf-8')
    object_key = b'selection/%(model)s/%(user_id)s/%(id)s.%(ext)s' % {
        b'model': builder.b_model,
        b'user_id': bytes(builder.b_user_id),
        b'id': selection.s_id,
        b'ext': ext,
    }

    upload_data = io.BytesIO()
    upload_data.write(selection.data)
    upload_data.seek(0)
    s3.upload_fileobj(upload_data, key=object_key.decode('utf-8'))

  def materialize(self, s3, wp10db, builder, content_type):
    params = json.loads(builder.b_params)

    selection = Selection(s_content_type=content_type,
                          s_builder_id=builder.b_id)
    selection.set_id()
    selection.data = self.build(content_type, **params)
    selection.set_updated_at_now()
    self._upload_to_storage(s3, selection, builder)

    logic_selection.insert_selection(wp10db, selection)

  def build(self, content_type, **params):
    raise NotImplementedError()

  def validate(self, **params):
    raise NotImplementedError()
