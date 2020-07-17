import json
import os
from os import path


class _Dir:
    def __init__(self, pth: str):
        self._path = pth
        self._loaded = {}

    def __getattr__(self, item: str):
        if not item or item[0] == '_':
            raise AttributeError(item)
        item = item.replace('_', '-')
        if item not in self._loaded:
            if path.isfile(path.join(self._path, f'{item}.json')):
                with open(path.join(self._path, f'{item}.json'), 'r') as f:
                    self._loaded[item] = json.load(f)
            else:
                self._loaded[item] = _Dir(path.join(self._path, item))
        return self._loaded[item]

    def __getitem__(self, item: str):
        return getattr(self, item)

    def __setitem__(self, item: str, value):
        item = item.replace('_', '-')
        self._loaded[item] = value
        os.makedirs(self._path, 0o755, exist_ok=True)
        with open(path.join(self._path, f'{item}.json'), 'w') as f:
            json.dump(value, f, ensure_ascii=False, indent=2)


_root = _Dir(path.join(path.dirname(__file__), 'data'))
__getattr__ = _root.__getattr__
