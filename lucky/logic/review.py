import time

from models.wp10.review import Review

def update_review_data(
        wp10_session, page_title, value, timestamp):
    timestamp_binary = time.strftime(
        '%Y-%m-%dT%H:%M:%SZ', timestamp.timetuple()).encode('utf-8')
    if value not in (b'GA', b'FA', b'FL'):
        raise ValueError('Unrecognized review value: %s' % value)

    review = wp10_session.query(Review).get(page_title)
    if review is None:
        review = Review(
            article=page_title, value=value, timestamp=timestamp_binary)
    else:
        review.article = page_title
        review.value = value
        review.timestamp = timestamp_binary
    wp10_session.add(review)
