import attr


@attr.s
class ZimFile:
  table_name = 'zim_files'

  z_id = attr.ib()
  z_selection_id = attr.ib()
  z_task_id = attr.ib()
  z_status = attr.ib(default='NOT_REQUESTED')
  z_version = attr.ib(default=None)
  z_requested_at = attr.ib(default=None)
  z_updated_at = attr.ib(default=None)
