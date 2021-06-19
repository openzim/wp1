import attr


@attr.s
class User:
  table_name = 'users'

  u_id = attr.ib()
  u_username = attr.ib()
