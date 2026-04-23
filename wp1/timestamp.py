from datetime import datetime, timezone, UTC


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def naive_utcnow():
    """naive UTC now"""
    return datetime.now(UTC).replace(tzinfo=None)
