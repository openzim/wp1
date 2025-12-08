import flask

from wp1.storage import connect_storage


def has_storage():
    return hasattr(flask.g, "storage")


def get_storage():
    if not has_storage():
        s3 = connect_storage()
        setattr(flask.g, "storage", s3)
    return getattr(flask.g, "storage")
