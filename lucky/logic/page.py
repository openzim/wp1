from models.wiki.page import Page

def get_pages_by_category(wiki_session, category, ns=None):
  q = wiki_session.query(Page).filter(Page.category == category)
  if ns is not None:
    q.filter(Page.namespace == ns)
  yield from q
