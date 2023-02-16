from wp1.credentials import CREDENTIALS, ENV
from wp1.logic import util
import wp1.logic.builder as logic_builder
import wp1.logic.selection as logic_selection

TASK_CPU = 2
TASK_MEMORY = 1024
TASK_DISK = 2048
MWOFFLINER_IMAGE = 'ghcr.io/openzim/mwoffliner:1.12.1'


def _get_params(wp10db, builder_id):
  if isinstance(builder_id, str):
    builder_id = builder_id.encode('utf-8')

  builder = logic_builder.get_builder(wp10db, builder_id)
  project = builder.b_project.decode('utf-8')
  selection = logic_builder.latest_selection_for(wp10db, builder_id,
                                                 'text/tab-separated-values')

  config = {
      'task_name': 'zimit',
      'warehouse_path': '/wp1',
      'image': {
          'name': MWOFFLINER_IMAGE.split(':')[0],
          'tag': MWOFFLINER_IMAGE.split(':')[1],
      },
      'resources': {
          'cpu': TASK_CPU,
          'memory': TASK_MEMORY,
          'disk': TASK_DISK,
      },
      'platform': None,
      'monitor': False,
      'flags': {
          'mwUrl': 'https://%s/' % project,
          'adminEmail': 'admin@wp1.openzim.org',
          'articleList': logic_selection.url_for_selection(selection),
          'customZimTitle': util.safe_name(builder.b_name.decode('utf-8')),
      }
  }

  return {
      'name': 'wp1_selection_%s' % selection.s_id.decode('utf-8'),
      'language': {
          'code': 'eng',
          'name_en': 'English',
          'name_native': 'English'
      },
      'category': 'other',
      'periodicity': 'manually',
      'tags': [],
      'enabled': True,
      'config': config,
  }
