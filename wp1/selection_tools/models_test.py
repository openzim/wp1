import unittest

from wp1.selection_tools.models import (
    PageMetrics,
    PageScoreWithRatings,
    decode_row,
    parse_page_metrics,
    parse_page_score_with_ratings,
)


class DecodeRowTest(unittest.TestCase):

    def test_decode_tuple(self):
        actual = decode_row((b"foo", 5, None, b"\xc3\xa9"))

        self.assertEqual(("foo", 5, None, "é"), actual)

    def test_decode_bytearray(self):
        actual = decode_row((bytearray(b"foo"),))

        self.assertEqual(("foo",), actual)

    def test_decode_mapping(self):
        actual = decode_row({"a": b"one", "b": 2})

        self.assertEqual(("one", 2), actual)


class ParsePageMetricsTest(unittest.TestCase):

    def test_with_ratings(self):
        actual = parse_page_metrics("Foo\t1\t100\t2\t3\t4\tProj=B:High\n")

        expected = PageMetrics("Foo", 1, 100, 2, 3, 4, ("Proj=B:High",))
        self.assertEqual(expected, actual)

    def test_without_ratings(self):
        actual = parse_page_metrics("Foo\t1\t100\t2\t3\t4\n")

        expected = PageMetrics("Foo", 1, 100, 2, 3, 4, ())
        self.assertEqual(expected, actual)

    def test_as_tsv_row(self):
        metrics = PageMetrics("Foo", 1, 100, 2, 3, 4, ("P=B:High", "Q=C:Low"))

        actual = metrics.as_tsv_row()

        expected = ("Foo", 1, 100, 2, 3, 4, "P=B:High", "Q=C:Low")
        self.assertEqual(expected, actual)


class ParsePageScoreWithRatingsTest(unittest.TestCase):

    def test_parse(self):
        actual = parse_page_score_with_ratings("Foo\t1\t100\t2\t3\t4\tP=B:High\n")

        expected = PageScoreWithRatings("Foo", 1, 100, 2, 3, 4, ("P=B:High",))
        self.assertEqual(expected, actual)

    def test_as_tsv_row(self):
        row = PageScoreWithRatings("Foo", 1, 100, 2, 3, 4, ("P=B:High",))

        actual = row.as_tsv_row()

        expected = ("Foo", 1, 100, 2, 3, 4, "P=B:High")
        self.assertEqual(expected, actual)
