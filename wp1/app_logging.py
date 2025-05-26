import logging

from wp1.credentials import CREDENTIALS, ENV


def configure_logging():
  creds = CREDENTIALS.get(ENV, {})
  log_config = creds.get('LOGGING', {})

  root_config = log_config.get('*', {
      'level': 'INFO',
      'format': '%(levelname)s:%(asctime)s:%(name)s:%(message)s',
  })

  # Convert the bare level string (ie 'DEBUG') to a logging level constant
  level_string = root_config.get('level', 'INFO')
  root_level = logging.getLevelNamesMapping().get(level_string.upper(),
                                                  logging.INFO)

  root_logger = logging.getLogger()
  root_logger.setLevel(root_level)
  formatter = logging.Formatter(
      root_config.get('format',
                      '%(levelname)s:%(asctime)s:%(name)s:%(message)s'))

  if not root_logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

  for logger_name, config in log_config.items():
    if logger_name == '*':
      continue
    level = config.get('level')
    if level is not None:
      level_enum = logging.getLevelNamesMapping().get(level.upper())
      if level_enum is not None:
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
