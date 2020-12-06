import os

import json

try:
  from wp1.credentials import CONF_LANG
except ImportError:
  # Default to English for unit tests.
  CONF_LANG = 'en'


def _get_conf_path():
  return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'conf',
                      CONF_LANG, 'conf.json')


_conf = None
with open(_get_conf_path()) as f:
  _conf = json.load(f)


def get_conf():
  return dict(_conf)
