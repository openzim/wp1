import unittest
from unittest.mock import MagicMock, patch

import wp1.logic.api.project as api_project


class TestApiProject(unittest.TestCase):
    page_text = (
        "{{ReleaseVersionParameters\n |hidden=yes\n |homepage="
        "Wikipedia:WikiProject Catholicism\n}}\n[[File:Juan de Juanes "
        "003.jpg|thumb|right|300px]]\nThis category contains "
        "subcategories of articles according to their currently "
        "assessed quality rating in the '''[[Wikipedia:WikiProject "
        "Catholicism|WikiProject Catholicism]]''' article assessment "
        "and rating scheme."
    )

    page_text_extra = (
        "{{ReleaseVersionParameters\n |hidden=yes\n |homepage="
        "Wikipedia:WikiProject Catholicism\n|extra1-title="
        "Foo Bar Baz\n|extra1-type=quality\n|extra1-category="
        "Category:Foo\n|extra1-ranking=300}}\n[[File:Juan de Juanes "
        "003.jpg|thumb|right|300px]]\nThis category contains "
        "subcategories of articles according to their currently "
        "assessed quality rating in the '''[[Wikipedia:WikiProject "
        "Catholicism|WikiProject Catholicism]]''' article assessment "
        "and rating scheme."
    )

    @patch("wp1.logic.api.project.api")
    def test_get_extra_assessments_homepage_only(self, patched_api):
        expected = {"extra": {}, "homepage": "Wikipedia:WikiProject Catholicism"}
        page = MagicMock()
        page.text.return_value = self.page_text
        patched_api.get_page.return_value = page

        actual = api_project.get_extra_assessments(b"Catholicism")
        self.assertEqual(expected, actual)

    @patch("wp1.logic.api.project.api")
    def test_get_extra_assessments_extra(self, patched_api):
        expected = {
            "extra": {
                "Foo": {
                    "title": "Foo Bar Baz",
                    "category": "Foo",
                    "ranking": "300",
                    "type": "quality",
                },
            },
            "homepage": "Wikipedia:WikiProject Catholicism",
        }
        page = MagicMock()
        page.text.return_value = self.page_text_extra
        patched_api.get_page.return_value = page

        actual = api_project.get_extra_assessments(b"Catholicism")
        self.assertEqual(expected, actual)
