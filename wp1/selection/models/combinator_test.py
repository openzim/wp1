from unittest.mock import MagicMock, patch

from wp1.base_db_test import BaseWpOneDbTest
from wp1.exceptions import Wp1FatalSelectionError, Wp1RetryableSelectionError
from wp1.models.wp10.builder import Builder
from wp1.models.wp10.selection import Selection
from wp1.selection.models.combinator import Builder as CombinatorBuilder
from wp1.selection.models.combinator import _fetch_selection_data


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


def _selection(status=b"OK", object_key=b"object-key"):
    return Selection(
        s_builder_id=b"builder-a",
        s_content_type=b"text/tab-separated-values",
        s_version=1,
        s_status=status,
        s_object_key=object_key,
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
                "Builder Builder A (builder-a) belongs to another user. You can only reference your own builders."
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
                "Builder Builder A (builder-a) belongs to project 'de.wikipedia.org'. All referenced builders must use the same project."
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
                "Builder Builder A (builder-a) is a combinator. Combinators can only reference leaf builders such as Simple, SPARQL, PetScan, Book, or WikiProject."
            ],
        )
        self.assertEqual(expected, actual)

    @patch("wp1.selection.models.combinator._fetch_selection_data")
    def test_build(self, mock_fetch_selection_data):
        data = {
            "builder-a": b"first article\r\nsecond\n# ignored\n",
            "builder-b": b"second\nthird\n",
            "builder-c": b"third\n",
        }
        mock_fetch_selection_data.side_effect = lambda _wp10db, _s3, builder_id: data[
            builder_id
        ]
        params = dict(self.params)
        params.update(
            include={"builders": ["builder-a", "builder-b"], "operation": "union"},
            exclude={"builders": ["builder-c"], "operation": "union"},
            s3=MagicMock(),
        )

        actual = self.builder.build("text/tab-separated-values", **params)

        self.assertEqual(b"first_article\nsecond", actual)

    @patch("wp1.selection.models.combinator._fetch_selection_data")
    def test_build_intersection(self, mock_fetch_selection_data):
        data = {
            "builder-a": b"first\nshared\n",
            "builder-b": b"second\nshared\n",
        }
        mock_fetch_selection_data.side_effect = lambda _wp10db, _s3, builder_id: data[
            builder_id
        ]
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

    @patch("wp1.selection.models.combinator._fetch_selection_data")
    def test_build_empty_result(self, mock_fetch_selection_data):
        mock_fetch_selection_data.return_value = b""
        params = dict(self.params)
        params.update(s3=MagicMock())

        with self.assertRaises(Wp1FatalSelectionError):
            self.builder.build("text/tab-separated-values", **params)

    @patch("wp1.selection.models.combinator.logic_builder.latest_selection_for")
    def test_fetch_selection_data(self, mock_latest_selection):
        mock_latest_selection.return_value = _selection()
        s3 = MagicMock()
        s3.download_fileobj.side_effect = lambda _key, buf: buf.write(b"first\n")

        actual = _fetch_selection_data(MagicMock(), s3, "builder-a")

        self.assertEqual(b"first\n", actual)
        s3.download_fileobj.assert_called_once()

    @patch("wp1.selection.models.combinator.logic_builder.latest_selection_for")
    def test_fetch_selection_data_failed_selection(self, mock_latest_selection):
        mock_latest_selection.return_value = _selection(status=b"FAILED")

        with self.assertRaises(Wp1FatalSelectionError):
            _fetch_selection_data(MagicMock(), MagicMock(), "builder-a")

    @patch("wp1.selection.models.combinator.logic_builder.latest_selection_for")
    def test_fetch_selection_data_retryable_selection(self, mock_latest_selection):
        mock_latest_selection.return_value = _selection(status=b"CAN_RETRY")

        with self.assertRaises(Wp1RetryableSelectionError):
            _fetch_selection_data(MagicMock(), MagicMock(), "builder-a")

    @patch("wp1.selection.models.combinator.logic_builder.latest_selection_for")
    def test_fetch_selection_data_missing_selection(self, mock_latest_selection):
        mock_latest_selection.return_value = None

        with self.assertRaises(Wp1RetryableSelectionError):
            _fetch_selection_data(MagicMock(), MagicMock(), "builder-a")

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
