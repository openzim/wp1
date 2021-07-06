import logging

import flask
from kiwixstorage import KiwixStorage

logger = logging.getLogger(__name__)

try:
  from wp1.credentials import CREDENTIALS, ENV
except ImportError:
  logger.exception('The file credentials.py must be populated manually in '
                   'order to connect to the backend storage system.')
  CREDENTIALS = None
  ENV = None


def has_storage():
  return hasattr(flask.g, 'storage')


def get_storage():
  if not has_storage():
    creds = CREDENTIALS[ENV]['STORAGE']
    connect_str = (
        'https://s3.us-west-1.wasabisys.com/'
        '?keyId=%(key)s&secretAccessKey=%(secret)s&bucketName=%(bucket)s' %
        creds)
    s3 = KiwixStorage(connect_str)
    s3.check_credentials(list_buckets=True, bucket=True, write=True, read=True)
    setattr(flask.g, 'storage', s3)
  return getattr(flask.g, 'storage')
