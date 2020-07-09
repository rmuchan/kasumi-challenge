import json
from os import path


class _Dir:
    def __init__(self, pth: str):
        self._path = pth
        self._loaded = {}

    def __getattr__(self, item: str):
        item = item.replace('_', '-')
        if item not in self._loaded:
            if path.isdir(path.join(self._path, item)):
                self._loaded[item] = _Dir(path.join(self._path, item))
            else:
                with open(path.join(self._path, f'{item}.json'), 'r') as f:
                    self._loaded[item] = json.load(f)
        return self._loaded[item]


_root = _Dir(path.join(path.dirname(__file__), 'data'))
__getattr__ = _root.__getattr__
