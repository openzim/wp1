import logging
import time

from wp1.models.wp10.review import Review

logger = logging.getLogger(__name__)


def insert_or_update_review_data(wp10_session, page_title, value, timestamp):
    timestamp_binary = time.strftime(
        "%Y-%m-%dT%H:%M:%SZ", timestamp.timetuple()
    ).encode("utf-8")
    if value not in (b"GA", b"FA", b"FL"):
        raise ValueError("Unrecognized review value: %s" % value)

    review = wp10_session.query(Review).get(page_title)
    if review is None:
        logging.info("New article found: %s", page_title.decode("utf-8"))
        review = Review(article=page_title, value=value, timestamp=timestamp_binary)
    else:
        logging.info("Updating article: %s", page_title.decode("utf-8"))
        review.article = page_title
        review.value = value
        review.timestamp = timestamp_binary
    wp10_session.add(review)


def delete_review_data(wp10_session, page_title, value):
    review = wp10_session.query(Review).get(page_title)
    if review.value != value:
        raise ValueError(
            "Review value of %s does not match given old value %s"
            % (review.value, value)
        )
    wp10_session.delete(review)
