from wp1.models.wp10.zim_file import ZimTask

def get_zim_task(wp10db, zim_task_id):
    """Retrieves a ZIM task by its ID. Returns a ZimTask or None."""
    with wp10db.cursor() as cursor:
        cursor.execute(
            'SELECT * FROM zim_tasks WHERE z_id = %s', (zim_task_id,)
        )
        row = cursor.fetchone()
    if not row:
        return None
    return ZimTask(**row)