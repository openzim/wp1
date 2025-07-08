from wp1.models.wp10.zim_file import ZimFile

def get_zim_file(wp10db, zim_file_id):
    """Retrieves a ZIM file by its ID. Returns a ZimFile or None."""
    with wp10db.cursor() as cursor:
        cursor.execute(
            'SELECT * FROM zim_files WHERE z_id = %s', (zim_file_id,)
        )
        row = cursor.fetchone()
    if not row:
        return None
    return ZimFile(**row)