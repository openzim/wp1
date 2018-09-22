from wp10_db import Session
from models.wp10.review import Review

session = Session()

q = session.query(Review).filter(Review.value==b'GA').limit(10)

for review in q:
    print(review)
