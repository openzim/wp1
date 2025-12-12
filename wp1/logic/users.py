"""Logic for user creation and management."""

from pymysql.connections import Connection


def create_or_update_user(wp10db, user_id, username, email=None):

    with wp10db.cursor() as cursor:
        cursor.execute(
            """
      INSERT INTO users (u_id, u_username, u_email)
      VALUES (%(u_id)s, %(u_username)s, %(u_email)s)
      ON DUPLICATE KEY UPDATE
        u_username = VALUES(u_username),
        u_email = VALUES(u_email)
      """,
            {"u_id": user_id, "u_username": username, "u_email": email},
        )
        wp10db.commit()


def user_exists(wp10db, user_id):

    with wp10db.cursor() as cursor:
        cursor.execute("SELECT 1 FROM users WHERE u_id = %s", (user_id,))
        return cursor.fetchone() is not None
