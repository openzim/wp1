import os

import json


def _get_conf_path():
  return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'conf.json')


_conf = None
with open(_get_conf_path()) as f:
  _conf = json.load(f)


def get_conf():
  return dict(_conf)
