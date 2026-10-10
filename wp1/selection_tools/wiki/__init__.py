from collections.abc import Generator
from collections import deque
import requests

from wp1.constants import WP1_USER_AGENT
from wp1.selection_tools.models import LangLink


def fetch_category_members(
    session: requests.Session,
    host: str,
    category_title: str,
    namespace: int,
) -> Generator[dict[str, str], None, None]:
    """Yield dicts with 'title' and 'ns' for every member of a category."""
    url = f"https://{host}/w/api.php"
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": category_title,
        "cmnamespace": f"14|{namespace}",  # subcategories + target namespace
        "cmlimit": "400",
        "format": "json",
    }
    while True:
        resp = session.get(url, params=params, headers={"User-Agent": WP1_USER_AGENT})
        resp.raise_for_status()
        data = resp.json()
        yield from data.get("query", {}).get("categorymembers", [])

        cmcontinue = data.get("continue", {}).get("cmcontinue")
        if not cmcontinue:
            return
        params["cmcontinue"] = cmcontinue


def generate_category_entries(
    lang_code: str,
    categories: list[str],
    namespace: int,
    max_depth: int,
    host: str = "wikipedia.org",
) -> Generator[str, None, None]:
    """BFS over a category and its subcategories, returning target-namespace titles."""
    host = f"{lang_code}.{host}"
    seen_categories = set()
    seen_titles: set[str] = set()
    queue = deque([(f"Category:{category}", 0) for category in categories])

    with requests.Session() as session:
        while queue:
            category, depth = queue.popleft()
            if depth >= max_depth or category in seen_categories:
                continue
            seen_categories.add(category)

            for member in fetch_category_members(session, host, category, namespace):
                title, ns = member["title"], member["ns"]
                if ns == 14:  # subcategory -> explore it
                    queue.append((title, depth + 1))
                elif ns == namespace:  # target namespace -> keep it
                    article = title.replace(" ", "_")
                    if article in seen_titles:
                        continue
                    seen_titles.add(article)
                    yield article


def generate_langlinks(
    lang_code: str, titles: list[str], languages: list[str]
) -> Generator[LangLink, None, None]:
    """Yield a LangLink for each language an article exists in."""
    url = f"https://{lang_code}.wikipedia.org/w/api.php"
    with requests.Session() as s:
        # Batch up to 50 titles
        for i in range(0, len(titles), 50):
            batch = titles[i : i + 50]
            data = s.get(
                url,
                params={
                    "action": "query",
                    "prop": "langlinks",
                    "titles": "|".join(batch),
                    "lllimit": "500",
                    "format": "json",
                },
                headers={"User-Agent": WP1_USER_AGENT},
            ).json()

            original = {n["to"]: n["from"] for n in data.get("normalized", [])}
            per_title: dict[str, dict[str, str]] = {}
            for page in data.get("query", {}).get("pages", {}).values():
                api_title = page.get("title", "")
                sent_title = original.get(api_title, api_title)
                per_title[sent_title] = {
                    ll["lang"]: ll["*"] for ll in page.get("langlinks", [])
                }

            for title in batch:
                langlinks = per_title.get(title, {})
                for language in languages:
                    if language in langlinks:
                        target = langlinks[language].replace(" ", "_")
                        yield LangLink(title, language, target)
