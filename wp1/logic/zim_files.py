from pymysql.connections import Connection

from wp1.models.wp10.zim_file import ZimTask


def get_zim_task(wp10db: Connection, z_id: int) -> ZimTask | None:
    """Retrieves a ZIM task by its ID. Returns a ZimTask or None."""
    with wp10db.cursor() as cursor:
        cursor.execute("SELECT * FROM zim_tasks WHERE z_id = %s", (z_id,))
        row = cursor.fetchone()
    if not row:
        return None
    return ZimTask(**row)


def get_zim_task_by_task_id(wp10db: Connection, task_id: str | bytes) -> ZimTask | None:
    """Retrieves a ZIM task by its task ID. Returns a ZimTask or None."""
    with wp10db.cursor() as cursor:
        cursor.execute("SELECT * FROM zim_tasks WHERE z_task_id = %s", (task_id,))
        row = cursor.fetchone()
    if not row:
        return None
    return ZimTask(**row)
