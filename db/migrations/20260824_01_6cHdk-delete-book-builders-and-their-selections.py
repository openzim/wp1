"""
Delete book builders and their selections

The Book builder was removed (https://github.com/openzim/wp1/issues/727), so
delete all existing builders that used it, along with their selections, ZIM
schedules and ZIM tasks. This is a destructive migration with no rollback.
"""

from yoyo import step

__depends__ = {
    "20250707_01_qY30l-add-title-to-zim-files-table",
    "20260823_01_add_dbname_to_builders",
}

BOOK_MODEL = "wp1.selection.models.book"

steps = [
    step(
        "DELETE zt FROM zim_tasks zt"
        "  JOIN selections s ON zt.z_selection_id = s.s_id"
        "  JOIN builders b ON s.s_builder_id = b.b_id"
        "  WHERE b.b_model = '%s'" % BOOK_MODEL
    ),
    step(
        "DELETE zs FROM zim_schedules zs"
        "  JOIN builders b ON zs.s_builder_id = b.b_id"
        "  WHERE b.b_model = '%s'" % BOOK_MODEL
    ),
    step(
        "DELETE s FROM selections s"
        "  JOIN builders b ON s.s_builder_id = b.b_id"
        "  WHERE b.b_model = '%s'" % BOOK_MODEL
    ),
    step("DELETE FROM builders WHERE b_model = '%s'" % BOOK_MODEL),
]
