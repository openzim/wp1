import json

_conf = None
with open('conf.json') as f:
    _conf = json.load(f)

def get_conf():
    return dict(_conf)
