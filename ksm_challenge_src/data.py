import json
import os
from os import path

from . import saves_updater


class _Dir:
    def __init__(self, pth: str, is_save: bool):
        self._path = pth
        self._is_save = is_save
        self._loaded = {}

    # 参与布尔运算时始终视为False，允许以"data.nonexistent or {}"的形式使用默认值
    def __bool__(self):
        return False

    def __getattr__(self, item: str):
        if not item or item[0] == '_':
            raise AttributeError(item)
        item = item.replace('_', '-')
        if item not in self._loaded:
            if path.isfile(path.join(self._path, f'{item}.json')):
                with open(path.join(self._path, f'{item}.json'), 'r') as f:
                    self._loaded[item] = json.load(f)
                    if self._is_save:
                        saves_updater.update(self._loaded[item])
            else:
                is_save = self._is_save or (self is data and item == 'saves')
                self._loaded[item] = _Dir(path.join(self._path, item), is_save)
        return self._loaded[item]

    def __getitem__(self, item: str):
        return getattr(self, item)

    def __setitem__(self, item: str, value):
        item = item.replace('_', '-')
        self._loaded[item] = value
        os.makedirs(self._path, 0o755, exist_ok=True)
        with open(path.join(self._path, f'{item}.json'), 'w') as f:
            if self._is_save:
                value['$version'] = saves_updater.current_version
            json.dump(value, f, ensure_ascii=False, indent=2)

    def dir(self):
        return [x[:-len('.json')] for x in os.listdir(self._path) if x.endswith('.json')]

    def reload(self):
        self._loaded.clear()


data = _Dir(path.join(path.dirname(__file__), 'data'), False)
__getattr__ = data.__getattr__
