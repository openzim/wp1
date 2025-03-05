import logging

from kiwixstorage import KiwixStorage

logger = logging.getLogger(__name__)

try:
  from wp1.credentials import CREDENTIALS, ENV
except ImportError:
  logger.exception('The file credentials.py must be populated manually in '
                   'order to connect to the backend storage system.')
  CREDENTIALS = None
  ENV = None


def connect_storage():
  if CREDENTIALS is None or ENV is None or CREDENTIALS[ENV].get(
      'STORAGE') is None:
    raise ValueError('storage (s3) credentials in ENV=%s are None' % ENV)
  creds = CREDENTIALS[ENV]['STORAGE']
  connect_str = (
      '%(url)s/?keyId=%(key)s&secretAccessKey=%(secret)s&bucketName=%(bucket)s'
      % creds)
  print(connect_str)
  s3 = KiwixStorage(connect_str)
  s3.check_credentials(list_buckets=True, bucket=True, write=True, read=True)
  return s3
