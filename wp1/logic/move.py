import attr

from wp1.models.wp10.move import Move


def get_move(wp10db, timestamp, old_namespace, old_article):
    with wp10db.cursor() as cursor:
        args_dict = {
            "m_timestamp": timestamp,
            "m_old_namespace": old_namespace,
            "m_old_article": old_article,
        }
        cursor.execute(
            """
        SELECT * FROM moves
        WHERE m_timestamp = %(m_timestamp)s AND
              m_old_namespace = %(m_old_namespace)s AND
              m_old_article = %(m_old_article)s
    """,
            args_dict,
        )
        db_move = cursor.fetchone()
        return Move(**db_move) if db_move else None


def insert(wp10db, move):
    with wp10db.cursor() as cursor:
        cursor.execute(
            """
        INSERT INTO moves
          (m_timestamp, m_old_namespace, m_old_article, m_new_namespace,
           m_new_article)
        VALUES
          (%(m_timestamp)s, %(m_old_namespace)s, %(m_old_article)s,
           %(m_new_namespace)s, %(m_new_article)s)
    """,
            attr.asdict(move),
        )
