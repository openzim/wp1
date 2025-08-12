import attr


@attr.s
class User:
  table_name = 'users'

  u_id: str = attr.ib()
  u_username: str = attr.ib()
  u_email_oauth: str = attr.ib(default=None)  # Email from OAuth provider
  u_email_custom: str = attr.ib(default=None)  # Custom email set by the user
