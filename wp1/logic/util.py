import datetime
import re
import time

from wp1.conf import get_conf
from wp1.constants import AssessmentKind, TS_FORMAT_WP10
from wp1.models.wp10.namespace import Namespace

config = get_conf()
CATEGORY_NS_STR = config['CATEGORY_NS']
BY_QUALITY_STR = config['BY_QUALITY']
BY_IMPORTANCE_STR = config['BY_IMPORTANCE']
BY_IMPORTANCE_ALT_STR = config['BY_IMPORTANCE_ALT']
ARTICLES_LABEL_STR = config['ARTICLES_LABEL']
DATABASE_WIKI_TS = config['DATABASE_WIKI_TS']


def wp10_timestamp_to_unix(ts):
  if ts is None:
    raise ValueError('Cannot convert None timestamp')
  dt = datetime.datetime.strptime(ts.decode('utf-8'), TS_FORMAT_WP10)
  dt = datetime.datetime(dt.year,
                         dt.month,
                         dt.day,
                         dt.hour,
                         dt.minute,
                         dt.second,
                         tzinfo=datetime.timezone.utc)
  return int((dt - datetime.datetime(
      1970, 1, 1, tzinfo=datetime.timezone.utc)).total_seconds())


def category_for_project_by_kind(project_name,
                                 kind,
                                 category_prefix=True,
                                 use_alt=False):
  if kind == AssessmentKind.QUALITY:
    kind_tag = BY_QUALITY_STR
  elif kind == AssessmentKind.IMPORTANCE:
    if use_alt:
      kind_tag = BY_IMPORTANCE_ALT_STR
    else:
      kind_tag = BY_IMPORTANCE_STR
  else:
    raise ValueError('Parameter kind must be one of QUALITY or IMPORTANCE')

  return_bytes = False
  if isinstance(project_name, bytes):
    return_bytes = True
    project_name = project_name.decode('utf-8')

  category = '%s_%s_%s' % (project_name, ARTICLES_LABEL_STR, kind_tag)

  if category_prefix:
    category = CATEGORY_NS_STR + ':' + category

  return category.encode('utf-8') if return_bytes else category


def is_namespace_acceptable(ns):
  if ns < 0 or ns == 2 or ns % 2 == 1:
    return False
  return True


def title_for_api(wp10db, namespace, title):
  title = title.decode('utf-8')
  ns_str = int_to_ns(wp10db)[namespace].decode('utf-8')
  return '%s:%s' % (ns_str, title)


_NS_TO_INT = None
_INT_TO_NS = None


def ns_to_int(wp10db):
  global _NS_TO_INT
  if _NS_TO_INT is not None:
    return _NS_TO_INT
  else:
    if _INT_TO_NS is not None:
      _NS_TO_INT = {v: k for k, v in _INT_TO_NS.items()}
      return _NS_TO_INT

    with wp10db.cursor() as cursor:
      cursor.execute(
          '''
          SELECT * FROM namespacename
          WHERE dbname=%(dbname)s
      ''', {'dbname': DATABASE_WIKI_TS.encode('utf-8')})
      _NS_TO_INT = dict((n['ns_name'], n['ns_id']) for n in cursor.fetchall())
    return _NS_TO_INT


def int_to_ns(wp10db):
  global _INT_TO_NS
  if _INT_TO_NS is None:
    _INT_TO_NS = {v: k for k, v in ns_to_int(wp10db).items()}
  return _INT_TO_NS


def safe_name(name):
  return ''.join(c for c in name if re.match(r'\w|\.|-|_', c)).strip()
