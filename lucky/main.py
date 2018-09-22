from db import Session
from models.page import Page

session = Session()

q = session.query(Page).filter(Page.page_namespace == 14).filter(
    Page.category == 'Wikipedia_1.0_assessments')

for page in q:
    print(page)
