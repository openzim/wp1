import unittest

from wp1.templates import importance_label


class ImportanceLabelTest(unittest.TestCase):
    def test_replaces_class_suffix(self):
        self.assertEqual("High-Importance", importance_label(b"High-Class"))
        self.assertEqual("Unknown-Importance", importance_label(b"Unknown-Class"))

    def test_accepts_str(self):
        self.assertEqual("Mid-Importance", importance_label("Mid-Class"))

    def test_no_class_suffix_unchanged(self):
        self.assertEqual("NotAClass", importance_label(b"NotAClass"))
