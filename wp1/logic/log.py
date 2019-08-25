import attr

from wp1.models.wp10.log import Log


def insert_or_update(wp10db, log):
  with wp10db.cursor() as cursor:
    cursor.execute(
        '''
        INSERT INTO logging
          (l_project, l_namespace, l_article, l_action, l_timestamp, l_old,
           l_new, l_revision_timestamp)
        VALUES
          (%(l_project)s, %(l_namespace)s, %(l_article)s, %(l_action)s,
           %(l_timestamp)s, %(l_old)s, %(l_new)s, %(l_revision_timestamp)s)
        ON DUPLICATE KEY UPDATE l_article = l_article
    ''', attr.asdict(log))
