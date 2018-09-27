from conf import get_conf
from constants import AssessmentKind

config = get_conf()
CATEGORY_NS_STR = config['CATEGORY_NS']
BY_QUALITY_STR = config['BY_QUALITY']
BY_IMPORTANCE_STR = config['BY_IMPORTANCE']
ARTICLES_LABEL_STR = config['ARTICLES_LABEL']

def category_for_project_by_kind(project_name, kind, category_prefix=True):
  if kind == AssessmentKind.QUALITY:
    kind_tag = BY_QUALITY_STR
  elif kind == AssessmentKind.IMPORTANCE:
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
