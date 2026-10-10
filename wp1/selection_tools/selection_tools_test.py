import pathlib
import tempfile
import unittest

from wp1.selection_tools import (
    read_lines_from_tsv_file,
    strip_prefix,
    write_tsv_rows_to_file,
)


class SelectionToolsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.tmp_path = pathlib.Path(self.tmp.name)

    def test_write_and_read_tsv_rows(self):
        fp = self.tmp_path / "out.tsv"
        with fp.open("w", encoding="utf-8") as f:
            write_tsv_rows_to_file(f, [("a", "b"), ("c", "d")])

        self.assertEqual(["a\tb", "c\td"], read_lines_from_tsv_file(fp))

    def test_write_tsv_rows_none_uses_null_value(self):
        fp = self.tmp_path / "out.tsv"
        with fp.open("w", encoding="utf-8") as f:
            write_tsv_rows_to_file(f, [("a", None), (None, None)])

        self.assertEqual(["a\t", "\t"], read_lines_from_tsv_file(fp))

    def test_write_tsv_rows_custom_null_value(self):
        fp = self.tmp_path / "out.tsv"
        with fp.open("w", encoding="utf-8") as f:
            write_tsv_rows_to_file(f, [("a", None)], null_value="NULL")

        self.assertEqual(["a\tNULL"], read_lines_from_tsv_file(fp))

    def test_write_tsv_rows_decodes_bytes(self):
        fp = self.tmp_path / "out.tsv"
        with fp.open("w", encoding="utf-8") as f:
            write_tsv_rows_to_file(f, [(b"\xc3\xa9", bytearray(b"x"))])

        self.assertEqual(["é\tx"], read_lines_from_tsv_file(fp))

    def test_write_tsv_rows_stringifies_other_values(self):
        fp = self.tmp_path / "out.tsv"
        with fp.open("w", encoding="utf-8") as f:
            write_tsv_rows_to_file(f, [(1, 2.5)])

        self.assertEqual(["1\t2.5"], read_lines_from_tsv_file(fp))

    def test_read_lines_from_tsv_file_strips_newlines(self):
        fp = self.tmp_path / "in.tsv"
        fp.write_text("a\nb\nc", encoding="utf-8")

        self.assertEqual(["a", "b", "c"], read_lines_from_tsv_file(fp))

    def test_strip_prefix(self):
        actual = strip_prefix({"Talk:Foo", "Talk:Bar", "Baz"}, "Talk:")

        self.assertEqual({"Foo", "Bar", "Baz"}, actual)

    def test_strip_prefix_only_strips_leading(self):
        actual = strip_prefix({"A Talk:B"}, "Talk:")

        self.assertEqual({"A Talk:B"}, actual)
