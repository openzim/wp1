import logging

from kiwixstorage import KiwixStorage
from wp1.config import get_settings

logger = logging.getLogger(__name__)


def connect_storage():
    settings = get_settings()
    if not settings.STORAGE_KEY or not settings.STORAGE_SECRET:
        raise ValueError(
            "storage (s3) credentials are not configured (STORAGE_KEY/STORAGE_SECRET)"
        )
    connect_str = (
        f"{settings.STORAGE_URL or ''}/?keyId={settings.STORAGE_KEY}"
        f"&secretAccessKey={settings.STORAGE_SECRET}"
        f"&bucketName={settings.STORAGE_BUCKET}"
    )
    s3 = KiwixStorage(connect_str)
    s3.check_credentials(list_buckets=True, bucket=True, write=True, read=True)
    return s3
