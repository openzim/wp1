from wp1.base_db_test import BaseWpOneDbTest
from wp1.exceptions import Wp1FatalSelectionError
from wp1.selection.models.wikiproject_query import Builder as WikiProjectQueryBuilder


class WikiProjectQueryTest(BaseWpOneDbTest):

    def setUp(self):
        super().setUp()
        self.builder = WikiProjectQueryBuilder()

        ratings = (
            ("Water_Elements", 0, "Ocëan", "FA-Class", "Top-Class"),
            ("Water_Elements", 0, "Lake", "B-Class", "Top-Class"),
            ("Water_Elements", 0, "Pond", "B-Class", "Low-Class"),
            ("Water_Elements", 0, "Puddle", "Unassessed-Class", "Low-Class"),
            ("Water_Elements", 14, "Famous_bodies_of_water", "B-Class", "Top-Class"),
            ("Water_Elements", 14, "Lakes", "Category-Class", "NA-Class"),
            ("Fire", 0, "Campfire", "B-Class", "Top-Class"),
        )
        categories = (
            ("Water_Elements", "quality", "FA-Class"),
            ("Water_Elements", "quality", "B-Class"),
            ("Water_Elements", "quality", "Category-Class"),
            ("Water_Elements", "importance", "Top-Class"),
            ("Water_Elements", "importance", "Low-Class"),
            ("Water_Elements", "importance", "NA-Class"),
        )
        with self.wp10db.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO ratings (r_project, r_namespace, r_article, r_quality,"
                " r_importance) VALUES (%s, %s, %s, %s, %s)",
                ratings,
            )
            cursor.executemany(
                "INSERT INTO projects (p_project, p_timestamp) VALUES (%s, 0)",
                ("Water_Elements", "Fire"),
            )
            cursor.executemany(
                "INSERT INTO categories (c_project, c_type, c_rating, c_replacement,"
                " c_category, c_ranking) VALUES (%s, %s, %s, '', '', 0)",
                categories,
            )
        self.wp10db.commit()

    def _build(self, **params):
        data = self.builder.build(
            "text/tab-separated-values", wp10db=self.wp10db, **params
        )
        return sorted(data.decode("utf-8").split("\n"))

    def test_build_whole_project(self):
        actual = self._build(wikiproject="Water Elements")
        self.assertEqual(["Lake", "Ocëan", "Pond", "Puddle"], actual)

    def test_build_quality(self):
        actual = self._build(wikiproject="Water Elements", quality="B-Class")
        self.assertEqual(["Lake", "Pond"], actual)

    def test_build_assessed_quality(self):
        actual = self._build(wikiproject="Water Elements", quality="Assessed-Class")
        self.assertEqual(["Lake", "Ocëan", "Pond"], actual)

    def test_build_importance(self):
        actual = self._build(wikiproject="Water Elements", importance="Top-Class")
        self.assertEqual(["Lake", "Ocëan"], actual)

    def test_build_quality_and_importance(self):
        actual = self._build(
            wikiproject="Water Elements", quality="B-Class", importance="Low-Class"
        )
        self.assertEqual(["Pond"], actual)

    def test_build_pattern(self):
        actual = self._build(wikiproject="Water Elements", pattern="P")
        self.assertEqual(["Pond", "Puddle"], actual)

    def test_build_empty_filters(self):
        actual = self._build(
            wikiproject="Water Elements", quality="", importance="", pattern=""
        )
        self.assertEqual(["Lake", "Ocëan", "Pond", "Puddle"], actual)

    def test_build_wrong_content_type(self):
        with self.assertRaises(Wp1FatalSelectionError):
            self.builder.build(
                "text/csv", wp10db=self.wp10db, wikiproject="Water Elements"
            )

    def test_build_missing_wp10db(self):
        with self.assertRaises(Wp1FatalSelectionError):
            self.builder.build("text/tab-separated-values", wikiproject="Fire")

    def test_build_missing_wikiproject(self):
        with self.assertRaises(Wp1FatalSelectionError):
            self.builder.build("text/tab-separated-values", wp10db=self.wp10db)

    def test_validate(self):
        actual = self.builder.validate(wp10db=self.wp10db, wikiproject="Fire")
        self.assertEqual((["Fire"], [], []), actual)

    def test_validate_spaces(self):
        actual = self.builder.validate(wp10db=self.wp10db, wikiproject="Water Elements")
        self.assertEqual((["Water Elements"], [], []), actual)

    def test_validate_filters(self):
        actual = self.builder.validate(
            wp10db=self.wp10db,
            wikiproject="Water Elements",
            quality="B-Class",
            importance="Low-Class",
        )
        self.assertEqual((["Water Elements"], [], []), actual)

    def test_validate_assessed_quality(self):
        actual = self.builder.validate(
            wp10db=self.wp10db, wikiproject="Water Elements", quality="Assessed-Class"
        )
        self.assertEqual((["Water Elements"], [], []), actual)

    def test_validate_unassessed_quality(self):
        actual = self.builder.validate(
            wp10db=self.wp10db,
            wikiproject="Water Elements",
            quality="Unassessed-Class",
        )
        self.assertEqual((["Water Elements"], [], []), actual)

    def test_validate_invalid_quality(self):
        actual = self.builder.validate(
            wp10db=self.wp10db, wikiproject="Water Elements", quality="great"
        )
        self.assertEqual(([], ["great"], ["Invalid quality or importance"]), actual)

    def test_validate_invalid_importance(self):
        actual = self.builder.validate(
            wp10db=self.wp10db, wikiproject="Water Elements", importance="High-Class"
        )
        self.assertEqual(
            ([], ["High-Class"], ["Invalid quality or importance"]), actual
        )

    def test_validate_other_project_class(self):
        actual = self.builder.validate(
            wp10db=self.wp10db, wikiproject="Fire", quality="FA-Class"
        )
        self.assertEqual(([], ["FA-Class"], ["Invalid quality or importance"]), actual)

    def test_validate_only_other_namespaces(self):
        actual = self.builder.validate(
            wp10db=self.wp10db,
            wikiproject="Water Elements",
            quality="Category-Class",
            importance="NA-Class",
        )
        self.assertEqual(([], [], ["No articles match these filters"]), actual)

    def test_validate_pattern_no_match(self):
        actual = self.builder.validate(
            wp10db=self.wp10db, wikiproject="Water Elements", pattern="Sea"
        )
        self.assertEqual(([], [], ["No articles match these filters"]), actual)

    def test_validate_unknown_project(self):
        actual = self.builder.validate(wp10db=self.wp10db, wikiproject="Lava")
        self.assertEqual(([], ["Lava"], ["The WikiProject does not exist"]), actual)

    def test_validate_missing_wikiproject(self):
        actual = self.builder.validate(wp10db=self.wp10db)
        self.assertEqual(([], [], ["Missing WikiProject"]), actual)

    def test_validate_missing_wp10db(self):
        with self.assertRaises(Wp1FatalSelectionError):
            self.builder.validate(wikiproject="Fire")
