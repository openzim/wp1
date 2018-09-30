from conf import get_conf
from constants import AssessmentKind
from models.wp10.namespace import Namespace

config = get_conf()
CATEGORY_NS_STR = config['CATEGORY_NS']
BY_QUALITY_STR = config['BY_QUALITY']
BY_IMPORTANCE_STR = config['BY_IMPORTANCE']
BY_IMPORTANCE_ALT_STR = config['BY_IMPORTANCE_ALT']
ARTICLES_LABEL_STR = config['ARTICLES_LABEL']
DATABASE_WIKI_TS = config['DATABASE_WIKI_TS']

def category_for_project_by_kind(
    project_name, kind, category_prefix=True, use_alt=False):
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

  category = '%s_%s_%s' % (
    project_name, ARTICLES_LABEL_STR, kind_tag)

  if category_prefix:
    category = CATEGORY_NS_STR + ':' + category

  if return_bytes:
    return category.encode('utf-8')
  else:
    return category

def is_namespace_acceptable(ns):
  if ns < 0 or ns == 2 or ns % 2 == 1:
    return False
  return True

def title_for_api(wp10_session, namespace, title):
  title = title.decode('utf-8')
  ns_str = int_to_ns(wp10_session)[namespace].decode('utf-8')
  return '%s:%s' % (ns_str, title)

_NS_TO_INT = None
_INT_TO_NS = None
def ns_to_int(wp10_session):
  global _NS_TO_INT
  if _NS_TO_INT is not None:
    return _NS_TO_INT
  else:
    if _INT_TO_NS is not None:
      _NS_TO_INT = {v: k for k, v in _INT_TO_NS.items()}
      return _NS_TO_INT

    _NS_TO_INT = dict((ns.name, ns.id) for ns in
                      wp10_session.query(Namespace).filter(
                        Namespace.dbname == DATABASE_WIKI_TS.encode('utf-8')))
    return _NS_TO_INT

def int_to_ns(wp10_session):
  global _INT_TO_NS
  if _INT_TO_NS is not None:
    return _INT_TO_NS
  else:
    _INT_TO_NS = {v: k for k, v in ns_to_int(wp10_session).items()}
    return _INT_TO_NS
