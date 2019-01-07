from lucky.models.wp10.move import Move

def get_move(wp10db, timestamp, old_namespace, old_article):
  with wp10db.cursor() as cursor:
    cursor.execute('SELECT * FROM ' + Move.table_name + '''
      WHERE m_timestamp = %(m_timestamp)s AND
            m_old_namespace = %(m_old_namespace)s AND
            m_old_article = %(m_old_article)s
    ''', {
      'm_timestamp': timestamp,
      'm_old_namespace': old_namespace,
      'm_old_article': old_article,
    })
    db_move = cursor.fetchone()
    if db_move:
      return Move(**db_move)
    else:
      return None


def insert(wp10db, move):
  raise NotImplementedError('Need to convert to db access')
