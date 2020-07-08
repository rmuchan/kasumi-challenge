import json
from os import path


_loaded = {}


def __getattr__(name: str):
    if name not in _loaded:
        with open(path.join(path.dirname(__file__), 'data', name + '.json'), 'r') as f:
            d = json.load(f)
            _loaded[name] = d
    return _loaded[name]
