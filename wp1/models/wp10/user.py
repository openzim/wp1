import attr


@attr.s
class User:
    table_name = "users"

    u_id: str = attr.ib()
    u_username: str = attr.ib()
    u_email: str = attr.ib(default=None)
