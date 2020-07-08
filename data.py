import json
from os import path


class _Dir:
    def __init__(self, pth: str):
        self._path = pth

    def __getattr__(self, item: str):
        item = item.replace('_', '-')
        key = path.join(self._path, item)
        if key not in _loaded:
            if path.isdir(key):
                _loaded[key] = _Dir(key)
            else:
                with open(path.join(self._path, f'{item}.json'), 'r') as f:
                    _loaded[key] = json.load(f)
        return _loaded[key]


_loaded = {}
_root = _Dir(path.join(path.dirname(__file__), 'data'))
__getattr__ = _root.__getattr__
