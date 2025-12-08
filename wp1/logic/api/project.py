from collections import defaultdict
import logging
import re

import mwparserfromhell

from wp1 import api
from wp1.conf import get_conf
from wp1.constants import AssessmentKind
from wp1.logic import util as logic_util

logger = logging.getLogger(__name__)

config = get_conf()
CATEGORY_NS_STR = config["CATEGORY_NS"]

RE_EXTRA = re.compile(r"extra(\d)-(.+)")


def get_extra_assessments(project_name):
    ans = {"extra": {}}
    page_name = logic_util.category_for_project_by_kind(
        project_name, AssessmentKind.QUALITY
    ).decode("utf-8")
    logging.debug("Retrieving page %s from API", page_name)
    page = api.get_page(page_name)
    if page is None:
        return ans

    text = page.text(section=0)
    wikicode = mwparserfromhell.parse(text)

    template = None
    for candidate_template in wikicode.filter_templates():
        if candidate_template.name.strip() == "ReleaseVersionParameters":
            template = candidate_template
            break

    if template is None:
        return ans

    for key in ("parent", "shortname", "homepage"):
        if template.has(key):
            ans[key] = template.get(key).value.strip()

    extra = defaultdict(dict)
    for param in template.params:
        md = RE_EXTRA.match(param.name.strip())
        if md:
            extra[md.group(1)][md.group(2)] = template.get(param.name).value.strip()

    for num_str, params in extra.items():
        if (
            "title" not in params
            or "type" not in params
            or "category" not in params
            or "ranking" not in params
        ):
            continue

        category = (
            params["category"].replace("%s:" % CATEGORY_NS_STR, "").replace(" ", "_")
        )
        params["category"] = category
        ans["extra"][category] = params

    return ans
