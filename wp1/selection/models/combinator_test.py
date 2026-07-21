from unittest.mock import MagicMock, patch

from wp1.base_db_test import BaseWpOneDbTest
from wp1.exceptions import (
    Wp1FatalMetaSelectionError,
    Wp1FatalSelectionError,
    Wp1MetaBuilderProcessError,
    Wp1RetryableMetaSelectionError,
    Wp1RetryableSelectionError,
)
from wp1.models.wp10.builder import Builder
from wp1.selection.models.combinator import Builder as CombinatorBuilder


def _reference_builder(
    id_="builder-a",
    name="Builder A",
    user_id="1234",
    project="en.wikipedia.org",
    model="wp1.selection.models.simple",
):
    return Builder(
        b_id=id_.encode("utf-8"),
        b_name=name.encode("utf-8"),
        b_user_id=str(user_id).encode("utf-8"),
        b_project=project.encode("utf-8"),
        b_model=model.encode("utf-8"),
        b_params=b"{}",
    )


class CombinatorBuilderTest(BaseWpOneDbTest):

    def setUp(self):
        super().setUp()
        self.builder = CombinatorBuilder()
        self.params = {
            "project": "en.wikipedia.org",
            "user_id": "1234",
            "wp10db": MagicMock(),
            "include": {"builders": ["builder-a"], "operation": "union"},
        }

    def _insert_builder(
        self,
        id_="builder-a",
        name="Builder A",
        user_id="1234",
        project="en.wikipedia.org",
        model="wp1.selection.models.simple",
        current_version=0,
    ):
        with self.wp10db.cursor() as cursor:
            cursor.execute(
                """INSERT INTO builders
                   (b_id, b_name, b_user_id, b_project, b_params, b_model,
                    b_created_at, b_updated_at, b_current_version,
                    b_selection_zim_version)
                   VALUES
                   (%s, %s, %s, %s, %s, %s,
                    '20260329180000', '20260329180000', %s, 0)
                """,
                (
                    id_.encode("utf-8"),
                    name.encode("utf-8"),
                    str(user_id).encode("utf-8"),
                    project.encode("utf-8"),
                    b'{"list": ["first"]}',
                    model.encode("utf-8"),
                    current_version,
                ),
            )
        self.wp10db.commit()

    def _insert_selection(self, id_, builder_id, object_key, version=1):
        with self.wp10db.cursor() as cursor:
            cursor.execute(
                """INSERT INTO selections
                   (s_id, s_builder_id, s_content_type, s_updated_at, s_version,
                    s_object_key, s_status, s_article_count)
                   VALUES
                   (%s, %s, %s, '20260329180000', %s, %s, 'OK', 1)
                """,
                (
                    id_.encode("utf-8"),
                    builder_id.encode("utf-8"),
                    b"text/tab-separated-values",
                    version,
                    object_key.encode("utf-8"),
                ),
            )
        self.wp10db.commit()

    @patch("wp1.selection.models.combinator.logic_builder.get_builder")
    def test_validate(self, mock_get_builder):
        mock_get_builder.return_value = _reference_builder()

        actual = self.builder.validate(**self.params)

        self.assertEqual(([], [], []), actual)

    def test_validate_empty_include(self):
        params = dict(self.params)
        params["include"] = {"builders": [], "operation": "union"}

        actual = self.builder.validate(**params)

        self.assertEqual(
            ([], [], ["Please add at least one builder to the Include group"]), actual
        )

    def test_validate_invalid_include_operation(self):
        params = dict(self.params)
        params["include"] = {"builders": ["builder-a"], "operation": "xor"}

        actual = self.builder.validate(**params)

        expected = (
            [],
            [],
            [
                "Please select a valid operation (union or intersection) for the Include group"
            ],
        )
        self.assertEqual(expected, actual)

    @patch("wp1.selection.models.combinator.logic_builder.get_builder")
    def test_validate_same_builder_in_include_and_exclude(self, mock_get_builder):
        mock_get_builder.return_value = _reference_builder()
        params = dict(self.params)
        params["include"] = {"builders": ["builder-a"], "operation": "union"}
        params["exclude"] = {"builders": ["builder-a"], "operation": "union"}

        actual = self.builder.validate(**params)

        expected = (
            [],
            [],
            ["Builders cannot be both included and excluded: Builder A"],
        )
        self.assertEqual(expected, actual)

    @patch("wp1.selection.models.combinator.logic_builder.get_builder")
    def test_validate_ignores_empty_exclude_operation(self, mock_get_builder):
        mock_get_builder.return_value = _reference_builder()
        params = dict(self.params)
        params["exclude"] = {"builders": [], "operation": "xor"}

        actual = self.builder.validate(**params)

        self.assertEqual(([], [], []), actual)

    @patch("wp1.selection.models.combinator.logic_builder.get_builder")
    def test_validate_cross_user_builder(self, mock_get_builder):
        mock_get_builder.return_value = _reference_builder(user_id="5678")

        actual = self.builder.validate(**self.params)

        expected = (
            [],
            [],
            [
                "Builder Builder A belongs to another user. You can only reference your own builders."
            ],
        )
        self.assertEqual(expected, actual)

    @patch("wp1.selection.models.combinator.logic_builder.get_builder")
    def test_validate_cross_project_builder(self, mock_get_builder):
        mock_get_builder.return_value = _reference_builder(project="de.wikipedia.org")

        actual = self.builder.validate(**self.params)

        expected = (
            [],
            [],
            [
                "Builder Builder A belongs to project 'de.wikipedia.org'. All referenced builders must use the same project."
            ],
        )
        self.assertEqual(expected, actual)

    @patch("wp1.selection.models.combinator.logic_builder.get_builder")
    def test_validate_meta_builder_reference(self, mock_get_builder):
        mock_get_builder.return_value = _reference_builder(
            model="wp1.selection.models.combinator"
        )

        actual = self.builder.validate(**self.params)

        expected = (
            [],
            [],
            [
                "Builder Builder A is a combinator. Combinators can only reference leaf builders such as Simple, SPARQL, PetScan, Book, or WikiProject."
            ],
        )
        self.assertEqual(expected, actual)

    @patch("wp1.logic.builder.get_builder")
    @patch("wp1.selection.models.combinator.Builder._fetch_selection_data")
    def test_build(self, mock_fetch_selection_data, mock_get_builder):
        mock_get_builder.return_value = _reference_builder()
        data = {
            "builder-a": b"first article\r\nsecond\n# ignored\n",
            "builder-b": b"second\nthird\n",
            "builder-c": b"third\n",
        }
        mock_fetch_selection_data.side_effect = (
            lambda _wp10db, _s3, builder_id, _label: data[builder_id]
        )
        params = dict(self.params)
        params.update(
            include={"builders": ["builder-a", "builder-b"], "operation": "union"},
            exclude={"builders": ["builder-c"], "operation": "union"},
            s3=MagicMock(),
        )

        actual = self.builder.build("text/tab-separated-values", **params)

        self.assertEqual(b"first_article\nsecond", actual)

    @patch("wp1.logic.builder.get_builder")
    @patch("wp1.selection.models.combinator.Builder._fetch_selection_data")
    def test_build_intersection(self, mock_fetch_selection_data, mock_get_builder):
        mock_get_builder.return_value = _reference_builder()
        data = {
            "builder-a": b"first\nshared\n",
            "builder-b": b"second\nshared\n",
        }
        mock_fetch_selection_data.side_effect = (
            lambda _wp10db, _s3, builder_id, _label: data[builder_id]
        )
        params = dict(self.params)
        params.update(
            include={
                "builders": ["builder-a", "builder-b"],
                "operation": "intersection",
            },
            s3=MagicMock(),
        )

        actual = self.builder.build("text/tab-separated-values", **params)

        self.assertEqual(b"shared", actual)

    @patch("wp1.logic.builder.get_builder")
    @patch("wp1.selection.models.combinator.Builder._fetch_selection_data")
    def test_build_empty_result(self, mock_fetch_selection_data, mock_get_builder):
        mock_get_builder.return_value = _reference_builder()
        mock_fetch_selection_data.return_value = b""
        params = dict(self.params)
        params.update(s3=MagicMock())

        with self.assertRaises(Wp1FatalSelectionError):
            self.builder.build("text/tab-separated-values", **params)

    @patch("wp1.selection.models.combinator.logic_builder.get_builder")
    @patch("wp1.selection.models.combinator.Builder._fetch_selection_data")
    def test_build_reports_all_retryable_dependency_failures(
        self, mock_fetch_selection_data, mock_get_builder
    ):
        mock_get_builder.side_effect = lambda _wp10db, builder_id: _reference_builder(
            id_=builder_id,
            name={
                "builder-a": "Builder A",
                "builder-b": "Builder B",
                "builder-c": "Builder C",
            }[builder_id],
        )

        def fetch_selection(_wp10db, _s3, builder_id, label):
            if builder_id in ("builder-a", "builder-b"):
                raise Wp1RetryableMetaSelectionError(
                    f"Referenced builder {label} is not ready",
                    code="REFERENCED_SELECTION_NOT_READY",
                    reason="latest selection is not ready yet",
                    action="Wait for this list to finish processing, then retry this Combinator.",
                )
            return b"ok\n"

        mock_fetch_selection_data.side_effect = fetch_selection
        params = dict(self.params)
        params.update(
            include={
                "builders": ["builder-a", "builder-b", "builder-c"],
                "operation": "union",
            },
            s3=MagicMock(),
        )

        with self.assertRaises(Wp1RetryableSelectionError) as context:
            self.builder.build("text/tab-separated-values", **params)

        self.assertIsInstance(context.exception.__cause__, Wp1MetaBuilderProcessError)
        self.assertEqual(3, mock_fetch_selection_data.call_count)
        message = str(context.exception)
        self.assertIn("Builder A is not ready", message)
        self.assertIn("Builder B is not ready", message)
        referenced_errors = context.exception.extra["referenced_builder_errors"]
        self.assertEqual(
            ["builder-a", "builder-b"],
            [error["builder_id"] for error in referenced_errors],
        )
        self.assertEqual(
            ["CAN_RETRY", "CAN_RETRY"],
            [error["status"] for error in referenced_errors],
        )

    @patch("wp1.selection.models.combinator.logic_builder.get_builder")
    @patch("wp1.selection.models.combinator.Builder._fetch_selection_data")
    def test_build_reports_mixed_dependency_failures_as_fatal(
        self, mock_fetch_selection_data, mock_get_builder
    ):
        mock_get_builder.side_effect = lambda _wp10db, builder_id: _reference_builder(
            id_=builder_id,
            name={
                "builder-a": "Builder A",
                "builder-b": "Builder B",
                "builder-c": "Builder C",
            }[builder_id],
        )

        def fetch_selection(_wp10db, _s3, builder_id, label):
            if builder_id == "builder-b":
                raise Wp1RetryableMetaSelectionError(
                    f"Referenced builder {label} is not ready",
                    code="REFERENCED_SELECTION_NOT_READY",
                    reason="latest selection is not ready yet",
                    action="Wait for this list to finish processing, then retry this Combinator.",
                )
            if builder_id == "builder-c":
                raise Wp1FatalMetaSelectionError(
                    f"Referenced builder {label} latest selection failed",
                    code="REFERENCED_SELECTION_FAILED",
                    reason="latest selection failed",
                    action="Open this list, fix the failed selection, then update this Combinator.",
                )
            return b"ok\n"

        mock_fetch_selection_data.side_effect = fetch_selection
        params = dict(self.params)
        params.update(
            include={"builders": ["builder-a", "builder-b"], "operation": "union"},
            exclude={"builders": ["builder-c"], "operation": "union"},
            s3=MagicMock(),
        )

        with self.assertRaises(Wp1FatalSelectionError) as context:
            self.builder.build("text/tab-separated-values", **params)

        self.assertIsInstance(context.exception.__cause__, Wp1MetaBuilderProcessError)
        self.assertEqual(3, mock_fetch_selection_data.call_count)
        message = str(context.exception)
        self.assertIn("Builder B is not ready", message)
        self.assertIn("Builder C latest selection failed", message)
        referenced_errors = context.exception.extra["referenced_builder_errors"]
        self.assertEqual(
            ["CAN_RETRY", "FAILED"],
            [error["status"] for error in referenced_errors],
        )
        fatal_error = referenced_errors[1]
        self.assertEqual("REFERENCED_SELECTION_FAILED", fatal_error["code"])
        self.assertIn("fix the failed selection", fatal_error["action"])

    def test_validate_with_referenced_builder_in_db(self):
        self._insert_builder()

        actual = self.builder.validate(
            project="en.wikipedia.org",
            user_id="1234",
            wp10db=self.wp10db,
            include={"builders": ["builder-a"], "operation": "union"},
        )

        self.assertEqual(([], [], []), actual)

    def test_validate_missing_builder_in_db(self):
        actual = self.builder.validate(
            project="en.wikipedia.org",
            user_id="1234",
            wp10db=self.wp10db,
            include={"builders": ["builder-a"], "operation": "union"},
        )

        expected = (
            [],
            [],
            [
                "Builder 'builder-a' no longer exists. Please remove it from this combinator."
            ],
        )
        self.assertEqual(expected, actual)

    def test_build_with_latest_selections_in_db(self):
        self._insert_builder(id_="builder-a", current_version=1)
        self._insert_builder(id_="builder-b", current_version=1)
        self._insert_selection("selection-a", "builder-a", "object-a")
        self._insert_selection("selection-b", "builder-b", "object-b")
        s3 = MagicMock()
        objects = {
            "object-a": b"first\nshared\n",
            "object-b": b"second\nshared\n",
        }
        s3.download_fileobj.side_effect = lambda key, buf: buf.write(objects[key])

        actual = self.builder.build(
            "text/tab-separated-values",
            wp10db=self.wp10db,
            s3=s3,
            include={
                "builders": ["builder-a", "builder-b"],
                "operation": "intersection",
            },
        )

        self.assertEqual(b"shared", actual)
