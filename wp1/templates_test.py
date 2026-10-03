import unittest
from datetime import datetime

import mwparserfromhell

from wp1 import logs
from wp1.templates import env, importance_label


class ImportanceLabelTest(unittest.TestCase):
    def test_replaces_class_suffix(self):
        self.assertEqual("High-Importance", importance_label(b"High-Class"))
        self.assertEqual("Unknown-Importance", importance_label(b"Unknown-Class"))

    def test_accepts_str(self):
        self.assertEqual("Mid-Importance", importance_label("Mid-Class"))

    def test_no_class_suffix_unchanged(self):
        self.assertEqual("NotAClass", importance_label(b"NotAClass"))


class LogTransclusionTest(unittest.TestCase):
    def test_headings_only_appear_on_standalone_log(self):
        rendered = env.get_template("log_section.jinja2").render(
            log_date="December 25, 2018",
            renamed=["Renamed article"],
            reassessed=["Reassessed article"],
            assessed=["Assessed article"],
            removed=["Removed article"],
            name={
                name: name
                for name in (
                    "Renamed article",
                    "Reassessed article",
                    "Assessed article",
                    "Removed article",
                )
            },
            talk={
                name: "Talk:" + name
                for name in (
                    "Reassessed article",
                    "Assessed article",
                    "Removed article",
                )
            },
            moved_name={"Renamed article": "New name"},
            l={
                "Reassessed article": {"quality": None, "importance": None},
                "Assessed article": {"quality": None, "importance": None},
            },
        )
        standalone = mwparserfromhell.parse(rendered)
        transcluded = mwparserfromhell.parse(rendered)
        for tag in standalone.filter_tags():
            if tag.tag == "noinclude":
                standalone.replace(tag, tag.contents)
        for tag in transcluded.filter_tags():
            if tag.tag == "noinclude":
                transcluded.remove(tag)
        self.assertEqual(
            ["December 25, 2018", "Renamed", "Reassessed", "Assessed", "Removed"],
            [str(h.title).strip() for h in standalone.filter_headings()],
        )
        self.assertEqual([], transcluded.filter_headings())
        self.assertEqual(standalone.filter_wikilinks(), transcluded.filter_wikilinks())
        self.assertEqual(
            [datetime(2018, 12, 25).date()],
            logs.live_page_dates_missing_from_logs(
                rendered, set(), datetime(2018, 12, 24)
            ),
        )
