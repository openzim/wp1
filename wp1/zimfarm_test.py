import attr

from wp1 import zimfarm
from wp1.base_db_test import BaseWpOneDbTest
from wp1.models.wp10.builder import Builder


class ZimFarmTest(BaseWpOneDbTest):

  def _insert_builder(self):
    value_dict = attr.asdict(self.builder)
    value_dict['b_current_version'] = 1
    value_dict['b_id'] = b'1a-2b-3c-4d'
    with self.wp10db.cursor() as cursor:
      cursor.execute(
          '''INSERT INTO builders
               (b_id, b_name, b_user_id, b_project, b_params, b_model, b_created_at,
                b_updated_at, b_current_version)
             VALUES
               (%(b_id)s, %(b_name)s, %(b_user_id)s, %(b_project)s, %(b_params)s,
                %(b_model)s, %(b_created_at)s, %(b_updated_at)s, %(b_current_version)s)
          ''', value_dict)
    self.wp10db.commit()
    return value_dict['b_id']

  def _insert_selection(self, id_):
    version = 1
    object_key = 'selections/foo/1234/name.tsv'
    content_type = 'text/tab-separated-values'
    builder_id = self.builder.b_id
    with self.wp10db.cursor() as cursor:
      cursor.execute(
          '''INSERT INTO selections
                (s_id, s_builder_id, s_updated_at, s_content_type, s_version, s_object_key)
              VALUES
                (%s, %s, '20191225044444', %s, %s, %s)''',
          (id_, builder_id, content_type, version, object_key))
    self.wp10db.commit()

  def setUp(self):
    super().setUp()
    self.builder = Builder(
        b_id=b'1a-2b-3c-4d',
        b_name=b'My Builder',
        b_user_id=1234,
        b_project=b'en.wikipedia.fake',
        b_model=b'wp1.selection.models.simple',
        b_params=b'{"list": ["a", "b", "c"]}',
        b_created_at=b'20191225044444',
        b_updated_at=b'20191225044444',
        b_current_version=1,
    )

  def test_get_params(self):
    self._insert_builder()
    self._insert_selection(b'abc-12345-def')

    actual = zimfarm._get_params(self.wp10db, self.builder.b_id)

    self.assertEqual(
        {
            'name': 'wp1_selection_abc-12345-def',
            'language': {
                'code': 'eng',
                'name_en': 'English',
                'name_native': 'English'
            },
            'category': 'other',
            'periodicity': 'manually',
            'tags': [],
            'enabled': True,
            'config': {
                'task_name': 'mwoffliner',
                'warehouse_path': '/wp1',
                'image': {
                    'name': 'ghcr.io/openzim/mwoffliner',
                    'tag': '1.12.1'
                },
                'resources': {
                    'cpu': 2,
                    'memory': 1024,
                    'disk': 2048
                },
                'platform': None,
                'monitor': False,
                'flags': {
                    'mwUrl':
                        'https://en.wikipedia.fake/',
                    'adminEmail':
                        'admin@wp1.openzim.org',
                    'articleList':
                        'http://credentials.not.found.fake/selections/foo/1234/name.tsv',
                    'customZimTitle':
                        'MyBuilder'
                }
            }
        }, actual)
