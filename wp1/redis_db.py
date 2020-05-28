from redis import Redis

try:
  from wp1.credentials import ENV, CREDENTIALS
except ImportError:
  logger.exception('The file credentials.py must be populated manually in '
                   'order to connect to Redis')
  ENV = None
  CREDENTIALS = None


def connect():
  creds = CREDENTIALS[ENV]['REDIS']
  return Redis(**creds)
