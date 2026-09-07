from collections.abc import Generator
from collections import deque
import requests

from wp1.constants import WP1_USER_AGENT


def fetch_category_members(
    session: requests.Session,
    lang_code: str,
    category_title: str,
    namespace: int,
) -> Generator[dict[str, str], None, None]:
    """Yield dicts with 'title' and 'ns' for every member of a category."""
    url = f"https://{lang_code}.wikipedia.org/w/api.php"
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
    lang_code: str, categories: list[str], namespace: int, max_depth: int
) -> Generator[str, None, None]:
    """BFS over a category and its subcategories, returning target-namespace titles."""
    seen_categories = set()
    queue = deque([(f"Category:{category}", 0) for category in categories])

    with requests.Session() as session:
        while queue:
            category, depth = queue.popleft()
            if depth >= max_depth or category in seen_categories:
                continue
            seen_categories.add(category)

            for member in fetch_category_members(
                session, lang_code, category, namespace
            ):
                title, ns = member["title"], member["ns"]
                if ns == 14:  # subcategory -> explore it
                    queue.append((title, depth + 1))
                elif ns == namespace:  # target namespace -> keep it
                    yield title


def generate_langlinks(
    lang_code: str, titles: list[str], languages: list[str]
) -> Generator[tuple[str, str, str], None, None]:
    """Yield 'source<TAB>lang<TAB>target' (underscore-normalized)."""
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

            norm = {n["to"]: n["from"] for n in data.get("normalized", [])}

            for page in data.get("query", {}).get("pages", {}).values():
                normalized = page.get("title", "")
                source = norm.get(normalized, normalized).replace(" ", "_")
                for ll in page.get("langlinks", []):
                    if ll["lang"] in languages:
                        yield source, ll["lang"], ll["*"].replace(" ", "_")
