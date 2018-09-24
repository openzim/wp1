from collections import defaultdict
import re

import mwparserfromhell

from api import site
from conf import get_conf

config = get_conf()
CATEGORY_NS_STR = config['CATEGORY_NS']
BY_QUALITY_STR = config['BY_QUALITY']
ARTICLES_LABEL_STR = config['ARTICLES_LABEL']

RE_EXTRA = re.compile('extra(\d)-(.+)')

def get_extra_assessments(project):
  page_name = '%s:%s_%s_%s' % (
    CATEGORY_NS_STR, project, ARTICLES_LABEL_STR, BY_QUALITY_STR)
  print(page_name)
  page = site.pages[page_name]
  text = page.text(section=0)
  wikicode = mwparserfromhell.parse(text)

  template = None
  for candidate_template in wikicode.filter_templates():
    if candidate_template.name.strip() == 'ReleaseVersionParameters':
      template = candidate_template
      break

  if template is None:
    return None

  ans = {'extra': defaultdict(dict)}
  for key in ('parent', 'shortname', 'homepage'):
    if template.has(key):
      ans[key] = template.get(key).value.strip()

  for param in template.params:
    md = RE_EXTRA.match(param.name.strip())
    if md:
      ans['extra'][md.group(1)][md.group(2)] = (
        template.get(param.name).value.strip())

  return ans
